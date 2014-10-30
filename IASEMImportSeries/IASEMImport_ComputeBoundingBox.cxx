#include "IASEMImportSeries.h"

// ITK includes
#include "itkImage.h"
#include "itkImageFileReader.h"
#include "itkFlipImageFilter.h"
#include "itkBoundingRegionImageSinc.h"

itk::ImageRegion<2> ComputeBoundingBox( const std::string &fname, bool flip )
{
  const unsigned int Dimension = 2;
  typedef unsigned char PixelType;
  typedef itk::Image<PixelType, Dimension> ImageType;

  typedef itk::ImageFileReader<ImageType> ReaderType;

  typedef itk::ImageSource<ImageType> BaseFilterType;
  typedef itk::FlipImageFilter<ImageType> FlipFilterType;

  InstancePointer<ReaderType> reader;
  reader->SetFileName(fname);
  BaseFilterType::Pointer lastFilter = reader.GetPointer();

  const bool axis[] = {false,true};
  const FlipFilterType::FlipAxesArrayType flipAxes(axis);
  InstancePointer<FlipFilterType> flipper;
  flipper->SetInput(reader->GetOutput());
  flipper->SetFlipAxes(flipAxes);
  flipper->FlipAboutOriginOff();

  if(flip)
    lastFilter = flipper.GetPointer();


  typedef itk::BoundingRegionImageSinc<ImageType> BoundingRegionFilter;
  InstancePointer<BoundingRegionFilter> boundingRegion;
  boundingRegion->SetInput(lastFilter->GetOutput());
  boundingRegion->UpdateLargestPossibleRegion();
  return boundingRegion->GetRegion();
}
