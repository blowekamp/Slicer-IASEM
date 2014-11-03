#include "itkImageFileWriter.h"
#include "itkPluginUtilities.h"
#include "IASEMImportSeriesCLP.h"

#include "IASEMImportSeries.h"

//#define USE_ITK_FUTURE
#ifdef USE_ITK_FUTURE
#include "itkFutureFlipImageFilter.h"
#include "itkFutureSliceBySliceImageFilter.h"
#include "itkFutureShrinkImageFilter.h"
namespace itk
{
using future::FlipImageFilter;
using future::SliceBySliceImageFilter;
using future::ShrinkImageFilter;
}
#else

#include "itkFlipImageFilter.h"
#include "itkSliceBySliceImageFilter.h"
#include "itkShrinkImageFilter.h"
#endif

#include "itkBinShrinkImageFilter.h"
#include "itkImageFileReader.h"
#include "itkImageSeriesReader.h"
#include "itkImageFileWriter.h"
#include "itkChangeInformationImageFilter.h"
#include "itkExtractImageFilter.h"
#include "itkResampleImageFilter.h"
#include "itkChangeInformationImageFilter.h"
#include "itkNearestNeighborInterpolateImageFunction.h"
#include "itkAffineTransform.h"
#include "itkStreamingImageFilter.h"
#include "itkCommand.h"

#include "itkPipelineMonitorImageFilter.h"

#include <list>
#include <string>


// KWSys glob
#include "itksys/Glob.hxx"
#include "itksys/SystemTools.hxx"

// Use an anonymous namespace to keep class types and function names
// from colliding when module is used as shared object module.  Every
// thing should be in an anonymous namespace except for the module
// entry point, e.g. main()
//
namespace
{

ModuleProcessInformation * _CLPProcessInformation = NULL;


void UpdateProgress( const std::string &message, float progress = 0.0, float stageProgress = 0.0 )
{
ModuleProcessInformation * MPI = _CLPProcessInformation;
if( MPI )
  {
  strncpy(MPI->ProgressMessage, message.c_str(), 1023);

  if( progress != 0.0 )
    {
    MPI->Progress = progress;
    }
  if( stageProgress != 0.0 )
    {
    MPI->StageProgress = stageProgress;
    }


  if (MPI->ProgressCallbackFunction
      && MPI->ProgressCallbackClientData)
    {
    (*(MPI->ProgressCallbackFunction))(MPI->ProgressCallbackClientData);
    }
  if (MPI->Abort)
    {
    itkGenericExceptionMacro( "Aborted!" );
    }
  }
}



std::vector<std::string> GetFileListFromDirectory(const char *inputDirectory)
{
  const std::string globExpression = std::string(inputDirectory)+"/*.tif";


  itksys::Glob glob;
  glob.RecurseOff();
  glob.FindFiles(globExpression.c_str());

  std::vector<std::string> outFiles = glob.GetFiles();
  std::sort(outFiles.begin(), outFiles.end());

  return outFiles;
}



const unsigned int Dimension = 3;
typedef unsigned char PixelType;
typedef itk::Image<PixelType, Dimension> ImageType;

typedef itk::ImageSeriesReader<ImageType> ReaderType;

typedef itk::ImageToImageFilter<ImageType,ImageType> BaseFilterType;
typedef itk::FlipImageFilter<ImageType> FlipFilterType;
typedef itk::ChangeInformationImageFilter<ImageType> ChangeFilterType;
typedef itk::ExtractImageFilter<ImageType,ImageType> ExtractFilterType;
typedef itk::SliceBySliceImageFilter<ImageType,ImageType> SliceBySliceFilterType;
typedef itk::BinShrinkImageFilter<ImageType,ImageType> BinFilterType;
typedef itk::ShrinkImageFilter<ImageType,ImageType> ShrinkFilterType;
typedef itk::StreamingImageFilter<ImageType,ImageType> StreamerFilterType;

typedef itk::PipelineMonitorImageFilter<ImageType> MonitorFilterType;

typedef SliceBySliceFilterType::InternalInputImageType ImageType2D;
typedef itk::NearestNeighborInterpolateImageFunction< ImageType2D, double >  InterpolatorType;
typedef itk::ResampleImageFilter<ImageType2D,ImageType2D> ResampleFilterType;


//  The following section of code implements a Command observer
//  used to monitor the evolution of the registration process.
//
template<typename T>
class CommandIterationUpdate :
    public itk::Command
{
public:
  typedef CommandIterationUpdate    Self;
  typedef itk::Command              Superclass;
  typedef itk::SmartPointer<Self>   Pointer;
  itkNewMacro( Self );

  const TransformListType *sliceTransforms;
  ResampleFilterType::Pointer resampler;

  typedef T CallerType;

  typedef const CallerType* CallerPointer;

  void Execute(itk::Object *caller, const itk::EventObject & event)
    {
      Execute( (const itk::Object *)caller, event);
    }
  void Execute(const itk::Object * object, const itk::EventObject & event)
    {
      CallerPointer sliceBySlice = dynamic_cast< const CallerType* >( object );
      if( sliceBySlice && itk::IterationEvent().CheckEvent( &event ) )
        {
        itk::IndexValueType s = sliceBySlice->GetSliceIndex();
        itk::Transform< double, 2, 2 >::Pointer tx = (*sliceTransforms)[s];
        resampler->SetTransform(tx);
        if (0)
          {
          std::cout << "Slice: " << s << std::endl;
          std::cout << "Transform: " << tx << std::endl;
          }
        }
      else
        {
        std::cout << "cast failed!" << std::endl;
        object->Print(std::cout);
        }
    }


protected:
  CommandIterationUpdate() { };

};




const unsigned int bin_default[] = {1,1,1};

itk::Image<unsigned char, 3>::Pointer ApplyAlignmentToStack( const std::vector<std::string> &sliceList,
                                                             const itk::Vector<double,3> &spacing,
                                                             const itk::ImageRegion<2> &bb,
                                                             const itk::FixedArray< unsigned int, 3 > binFactors = bin_default,
                                                             bool enableZBinning = true,
                                                             const TransformListType &sliceTransforms = TransformListType(),
                                                             itk::Point<double, 3> pt1 = itk::Point<double, 3>(),
                                                             itk::Point<double, 3> pt2 = itk::Point<double, 3>()
  )
{

  std::vector<BaseFilterType::Pointer> filterStack(10);

  InstancePointer<ReaderType> reader;
  reader->SetFileNames(sliceList);
  reader->UseStreamingOn();
  reader->UpdateOutputInformation();

  ImageType::RegionType extractRegion = reader->GetOutput()->GetLargestPossibleRegion();
  for (unsigned int i = 0; i < 2; ++i)
    {
    extractRegion.SetIndex(i, bb.GetIndex(i));
    extractRegion.SetSize(i, bb.GetSize(i));
    }

  InstancePointer<ExtractFilterType> extractor;
  extractor->SetInput(reader->GetOutput());
  extractor->SetExtractionRegion(extractRegion);
  extractor->InPlaceOn();

  const bool axis[] = {false,true};
  const FlipFilterType::FlipAxesArrayType flipAxes(axis);
  InstancePointer<FlipFilterType> flipper;
  flipper->SetInput(extractor->GetOutput());
  flipper->SetFlipAxes(flipAxes);
  flipper->FlipAboutOriginOff();
  BaseFilterType::Pointer lastFilter = flipper.GetPointer();

  typedef CommandIterationUpdate<SliceBySliceFilterType> CommandType;
  InstancePointer<CommandType> observer;

  InstancePointer<InterpolatorType> interpolator;
  InstancePointer<ResampleFilterType> resampler;
  InstancePointer<itk::ChangeInformationImageFilter<ImageType2D> > sliceChanger;

  InstancePointer<SliceBySliceFilterType> sliceBySliceFilter;


  if ( sliceTransforms.size() == sliceList.size() )
    {
    const ImageType2D::SpacingType spacing(1.0);
    sliceChanger->SetOutputSpacing(spacing);
    sliceChanger->ChangeSpacingOn();

    const ImageType2D::PointType origin(0.0);
    sliceChanger->SetOutputOrigin(origin);
    sliceChanger->ChangeOriginOn();

    lastFilter->UpdateOutputInformation();
    itk::ImageRegion<2> region2d = lastFilter->GetOutput()->GetLargestPossibleRegion().Slice(2);
    resampler->SetInterpolator(interpolator);
    resampler->SetOutputStartIndex( region2d.GetIndex() );
    resampler->SetSize( region2d.GetSize() );
    resampler->SetInput(sliceChanger->GetOutput());

    sliceBySliceFilter->SetInput(lastFilter->GetOutput());
    sliceBySliceFilter->SetInputFilter(sliceChanger);
    sliceBySliceFilter->SetOutputFilter(resampler);

    observer->sliceTransforms = &sliceTransforms;
    observer->resampler = resampler;
    sliceBySliceFilter->AddObserver( itk::IterationEvent(), observer );

    lastFilter = sliceBySliceFilter;
    }

#ifndef NDEBUG
  InstancePointer<MonitorFilterType> monitor;
  monitor->SetInput(lastFilter->GetOutput());
  lastFilter = monitor.GetPointer();
#endif

  InstancePointer<ChangeFilterType> changer;
  changer->SetInput(lastFilter->GetOutput());
  changer->ChangeSpacingOn();
  changer->SetOutputSpacing(spacing);
  lastFilter = changer;

  InstancePointer<BinFilterType> binner;
  InstancePointer<ShrinkFilterType> shrinker;
  if (binFactors[0] != bin_default[0] ||
      binFactors[1] != bin_default[1] ||
      ( binFactors[2] != bin_default[2]  && enableZBinning ) )
    {
    binner->SetInput(lastFilter->GetOutput());
    binner->SetShrinkFactor(0, binFactors[0]);
    binner->SetShrinkFactor(1, binFactors[1]);

    if (enableZBinning)
      {
      binner->SetShrinkFactor(2, binFactors[2]);
      }
    lastFilter=binner.GetPointer();
    }


  if (binFactors[2] != bin_default[2] && !enableZBinning )
    {
    shrinker->SetInput(lastFilter->GetOutput());
    shrinker->SetShrinkFactor(2, binFactors[2]);
    lastFilter=shrinker.GetPointer();
    }


  lastFilter->UpdateOutputInformation();
  InstancePointer<ExtractFilterType> extractor2;
  if ( (pt1-pt2).GetNorm() >= lastFilter->GetOutput()->GetSpacing().GetNorm() )
    {
    itk::Index<3> idx1, idx2;
    lastFilter->GetOutput()->TransformPhysicalPointToIndex(pt1, idx1);
    lastFilter->GetOutput()->TransformPhysicalPointToIndex(pt2, idx2);

    for (unsigned int i = 0; i < 3; ++i)
      {
      if (idx1[i] > idx2[i])
        {
        const itk::IndexValueType t = idx1[i];
        idx1[i] = idx2[i];
        idx2[i] = t;
        }
      }
    itk::ImageRegion<3> crop;
    crop.SetIndex(idx1);
    crop.SetUpperIndex(idx2);
    std::cout << crop;
    crop.Crop(lastFilter->GetOutput()->GetLargestPossibleRegion());
    std::cout << crop;

    extractor2->SetInput(lastFilter->GetOutput());
    extractor2->SetExtractionRegion(crop);
    extractor2->InPlaceOn();
    lastFilter = extractor2;
    }

  lastFilter->UpdateOutputInformation();
  itk::SizeValueType numberOfStreamDivisions = lastFilter->GetOutput()->GetLargestPossibleRegion().GetSize(2);

  InstancePointer<StreamerFilterType> streamer;
  streamer->SetInput(lastFilter->GetOutput());
  streamer->SetNumberOfStreamDivisions(numberOfStreamDivisions);

  itk::PluginFilterWatcher watcher(streamer, "Stream Reading", _CLPProcessInformation, 0.5, 0.5);
  streamer->UpdateLargestPossibleRegion();

#ifndef NDEBUG
  std::cout << monitor;
#endif
  return streamer->GetOutput();
}

} // end of anonymous namespace

int main( int argc, char * argv[] )
{
  const double zeros[] =  {0.0,0.0,0.0};

  try
    {
    PARSE_ARGS;

    _CLPProcessInformation = CLPProcessInformation;

    //
    // Parameters to ApplyAlignemntToStack
    //
    std::vector<std::string> sliceList = GetFileListFromDirectory(inputDirectory.c_str());

    itk::Vector<double, 3> spacing;
    spacing.Fill(1.0);

    itk::ImageRegion<2> reduced_bb;

    itk::FixedArray< unsigned int, 3 > binFactorsArray;

    TransformListType sliceTransforms;

    itk::Point<double, 3> p1(zeros);
    itk::Point<double, 3> p2(zeros);

    // end

    if (imageROI.size()==6)
      {
      double c[3] = {0.0,0.0,0.0};
      double r[3] = {0.0,0.0,0.0};

      // the input is a 6 element vector containing the center in RAS space
      // followed by the radius in real world coordinates

      // copy out center values
      std::copy(imageROI.begin(), imageROI.begin() + 3, c );
      // copy out radius values
      std::copy(imageROI.begin() + 3, imageROI.end(), r );

      // create lower point
      p1[0] = -c[0] + r[0];
      p1[1] = -c[1] + r[1];
      p1[2] = c[2] + r[2];

      // create upper point
      p2[0] = -c[0] - r[0];
      p2[1] = -c[1] - r[1];
      p2[2] = c[2] - r[2];

      }

    if (imodXG.size())
      {
      // TODO check if file is valid
      sliceTransforms = ReadXGTransform( imodXG );
      }

    UpdateProgress("Extracting meta-data...", 0.0);
    ExtractFibicsInfo(sliceList, spacing, reduced_bb);

    if (!reduced_bb.GetSize(0) || !reduced_bb.GetSize(1))
      {

      float progress = 0.001;
      std::vector<std::string>::const_iterator  s_iter = sliceList.begin();
      UpdateProgress( itksys::SystemTools::GetFilenameName(*s_iter), 0.5*progress );
      UpdateProgress(std::string("File: ") + *s_iter, 0.5*progress);
      reduced_bb =  ComputeBoundingBox(*s_iter,false);
      progress += 1.0/sliceList.size();
      UpdateProgress(itksys::SystemTools::GetFilenameName(*s_iter), 0.5*progress, 1.0 );
      std::cout << reduced_bb;

      while (s_iter != sliceList.end())
        {

        UpdateProgress( itksys::SystemTools::GetFilenameName(*s_iter), 0.5*progress, 0.001 );
        const itk::ImageRegion<2> bb = ComputeBoundingBox(*s_iter,false);
        progress +=  1.0/sliceList.size();
        UpdateProgress(itksys::SystemTools::GetFilenameName(*s_iter), 0.5*progress, 1.0 );
        std::cout << bb << std::endl;

        const itk::Index<2> start = reduced_bb.GetIndex();
        itk::Index<2> upper = reduced_bb.GetUpperIndex();
        for (unsigned int i = 0; i < 2; ++i)
          {
          reduced_bb.SetIndex(i, std::min( start[i], bb.GetIndex()[i]) );
          upper[i] = std::max( upper[i], bb.GetUpperIndex()[i]);
          }
        reduced_bb.SetUpperIndex(upper);

        ++s_iter;
        }
      }

    std::cout << "Global Bounding Box: " << reduced_bb;


    binFactorsArray[0] = binFactors[0];
    binFactorsArray[1] = binFactors.size()<3?binFactors[0]:binFactors[1];
    binFactorsArray[2] = binFactors.size()==1?1:binFactors.back();

    typedef itk::Image<unsigned char, 3> ImageType;
    ImageType::Pointer out = ApplyAlignmentToStack( sliceList,
                                                    spacing,
                                                    reduced_bb,
                                                    binFactorsArray,
                                                    !disableZBin,
                                                    sliceTransforms,
                                                    p1,p2);

    typedef itk::ImageFileWriter<ImageType> WriterType;
    InstancePointer<WriterType> writer;
    writer->SetFileName( outputVolume.c_str() );
    writer->SetInput( out );
    writer->SetUseCompression(0);
    writer->Update();


    return EXIT_SUCCESS;
    }
  catch(std::exception &e)
    {
    std::cerr << "Exception: " << e.what() << std::endl;
    }
  catch(...)
    {
    std::cerr << "Unknown exception occurred!" << std::endl;
    }
  return EXIT_FAILURE;
}
