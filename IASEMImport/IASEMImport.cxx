#include "itkImageFileReader.h"
#include "itkImageFileWriter.h"
#include "itkBinShrinkImageFilter.h"
#include "itkShrinkImageFilter.h"
#include "itkExtractImageFilter.h"
#include "itkStreamingImageFilter.h"

#include "itkPipelineMonitorImageFilter.h"

#include "itkPluginUtilities.h"

#include "IASEMImportCLP.h"

// Use an anonymous namespace to keep class types and function names
// from colliding when module is used as shared object module.  Every
// thing should be in an anonymous namespace except for the module
// entry point, e.g. main()
//
namespace
{

// \brief A convient class to simplify the definition and creation of
// itk objects as pointers.
//
// Simply added the default constuctor of the pointer is to call the
// object's New() method.
//
//  Example Usage:
// \code
// itk::InstancePointer< itk::Image<unsigned char, 3> > image3d;
// \endcode
template<typename T>
struct InstancePointer
  : public T::Pointer
{
  typedef typename T::Pointer SuperClass;
  typedef T                   ObjectType;
  InstancePointer( void )
    : SuperClass( ObjectType::New() ) {}
};


template <class T>
int DoIt( int argc, char * argv[], T )
{
  PARSE_ARGS;

  itk::FixedArray< unsigned int, 3 > binFactorsArray;
  binFactorsArray[0] = binFactors[0];
  binFactorsArray[1] = binFactors.size()<3?binFactors[0]:binFactors[1];
  binFactorsArray[2] = binFactors.size()==1?1:binFactors.back();

  typedef    T InputPixelType;
  typedef    T OutputPixelType;

  typedef itk::Image<InputPixelType,  3> InputImageType;
  typedef itk::Image<OutputPixelType, 3> OutputImageType;


  typedef itk::ImageFileReader<InputImageType>  ReaderType;
  InstancePointer<ReaderType> reader;
  reader->UseStreamingOn();
  reader->SetFileName( input.c_str() );
  reader->UpdateOutputInformation();

  typedef itk::ImageSource<InputImageType> BaseFilterType;
  typename BaseFilterType::Pointer lastFilter = reader.GetPointer();


  typedef itk::ExtractImageFilter<InputImageType,InputImageType> ExtractFilterType;
  InstancePointer<ExtractFilterType> extractor;

  if (imageROI.size()==6)
    {
    itk::Point<double, 3> pt1;
    itk::Point<double, 3> pt2;

    double c[3] = {0.0,0.0,0.0};
    double r[3] = {0.0,0.0,0.0};

    // the input is a 6 element vector containing the center in RAS space
    // followed by the radius in real world coordinates

    // copy out center values
    std::copy(imageROI.begin(), imageROI.begin() + 3, c );
    // copy out radius values
    std::copy(imageROI.begin() + 3, imageROI.end(), r );

    // create lower point
    pt1[0] = -c[0] + r[0];
    pt1[1] = -c[1] + r[1];
    pt1[2] = c[2] + r[2];

    // create upper point
    pt2[0] = -c[0] - r[0];
    pt2[1] = -c[1] - r[1];
    pt2[2] = c[2] - r[2];

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
      crop.Crop(lastFilter->GetOutput()->GetLargestPossibleRegion());

      extractor->SetInput(lastFilter->GetOutput());
      extractor->SetExtractionRegion(crop);
      extractor->InPlaceOn();
      lastFilter = extractor;
      }
    }

#ifndef DEBUG
  typedef itk::PipelineMonitorImageFilter<InputImageType> MonitorFilterType;
  InstancePointer<MonitorFilterType> monitor;
  monitor->SetInput(lastFilter->GetOutput());
  lastFilter = monitor.GetPointer();
#endif


  typedef itk::BinShrinkImageFilter< InputImageType, InputImageType>  BinFilterType;
  typedef itk::ShrinkImageFilter< InputImageType, InputImageType> ShrinkFilterType;

  InstancePointer<BinFilterType> binner;
  InstancePointer<ShrinkFilterType> shrinker;

  if ( binFactorsArray[0] != 1 &&
       binFactorsArray[1] != 1 )
    {
    binner->SetInput(lastFilter->GetOutput());
    binner->SetShrinkFactor(0, binFactorsArray[0]);
    binner->SetShrinkFactor(1, binFactorsArray[1]);

    if (!disableZBin)
      binner->SetShrinkFactor(2, binFactorsArray[2]);
    lastFilter=binner.GetPointer();
    }


  if ( binFactorsArray[2] != 1 && disableZBin )
    {
    shrinker->SetInput(lastFilter->GetOutput());
    shrinker->SetShrinkFactor(2, binFactorsArray[2]);
    lastFilter=shrinker.GetPointer();
    }

#ifndef DEBUG
  InstancePointer<MonitorFilterType> monitor2;
  monitor2->SetInput(lastFilter->GetOutput());
  lastFilter = monitor2.GetPointer();
#endif


  lastFilter->UpdateOutputInformation();
  itk::SizeValueType numberOfStreamDivisions = lastFilter->GetOutput()->GetLargestPossibleRegion().GetSize(2);

  try
    {


    typename itk::ImageIOBase::Pointer imageio = itk::ImageIOFactory::CreateImageIO(outputVolume.c_str(),
                                                                                    itk::ImageIOFactory::WriteMode);

    typedef itk::ImageFileWriter<OutputImageType> WriterType;
    typename WriterType::Pointer writer = WriterType::New();
    writer->SetFileName( outputVolume.c_str() );
    writer->SetUseCompression(0);
    writer->SetImageIO(imageio);

    if ( imageio.IsNotNull() && imageio->CanStreamWrite() )
      {
      itk::PluginFilterWatcher watcher(writer.GetPointer(), "Stream Writing", CLPProcessInformation);

      writer->SetInput(lastFilter->GetOutput());
      writer->SetNumberOfStreamDivisions(numberOfStreamDivisions);
      writer->Update();
      }
    else
      {
      typedef itk::StreamingImageFilter<InputImageType,OutputImageType> StreamerFilterType;
      InstancePointer<StreamerFilterType> streamer;
      streamer->SetInput(lastFilter->GetOutput());
      streamer->SetNumberOfStreamDivisions(numberOfStreamDivisions);

      itk::PluginFilterWatcher watcher(streamer.GetPointer(), "Stream Reading", CLPProcessInformation);

      writer->SetInput(streamer->GetOutput());
      writer->Update();
      }
    }
  catch (...)
    {
#ifndef DEBUG
    std::cout << monitor;
    std::cout << monitor2;
#endif
    throw;
    }

  return EXIT_SUCCESS;
}

} // end of anonymous namespace


int main( int argc, char * argv[] )
{
  itk::ImageIOBase::IOPixelType     pixelType;
  itk::ImageIOBase::IOComponentType componentType;

  try
    {
    PARSE_ARGS;

    itk::GetImageType(input, pixelType, componentType);

    // This filter handles all types on input, but only produces
    // signed types
    switch( componentType )
      {
      case itk::ImageIOBase::UCHAR:
        return DoIt( argc, argv, static_cast<unsigned char>(0) );
        break;
      case itk::ImageIOBase::CHAR:
        return DoIt( argc, argv, static_cast<char>(0) );
        break;
      case itk::ImageIOBase::USHORT:
        return DoIt( argc, argv, static_cast<unsigned short>(0) );
        break;
      case itk::ImageIOBase::SHORT:
        return DoIt( argc, argv, static_cast<short>(0) );
        break;
      case itk::ImageIOBase::UINT:
        return DoIt( argc, argv, static_cast<unsigned int>(0) );
        break;
      case itk::ImageIOBase::INT:
        return DoIt( argc, argv, static_cast<int>(0) );
        break;
      case itk::ImageIOBase::ULONG:
        return DoIt( argc, argv, static_cast<unsigned long>(0) );
        break;
      case itk::ImageIOBase::LONG:
        return DoIt( argc, argv, static_cast<long>(0) );
        break;
      case itk::ImageIOBase::FLOAT:
        return DoIt( argc, argv, static_cast<float>(0) );
        break;
      case itk::ImageIOBase::DOUBLE:
        return DoIt( argc, argv, static_cast<double>(0) );
        break;
      case itk::ImageIOBase::UNKNOWNCOMPONENTTYPE:
      default:
        std::cout << "unknown component type" << std::endl;
        break;
      }
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

