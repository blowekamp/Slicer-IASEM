/*=========================================================================

  Program:   Insight Segmentation & Registration Toolkit
  Module:    $RCSfile: itkBinShrinkImageFilter.h,v $
  Language:  C++
  Date:      $Date: 2009-03-27 15:05:20 $
  Version:   $Revision: 1.45 $

  Copyright (c) Insight Software Consortium. All rights reserved.
  See ITKCopyright.txt or http://www.itk.org/HTML/Copyright.htm for details.

  Portions of this code are covered under the VTK copyright.
  See VTKCopyright.txt or http://www.kitware.com/VTKCopyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notices for more information.

=========================================================================*/
#ifndef __itkBinShrinkImageFilter_h
#define __itkBinShrinkImageFilter_h

#include "itkShrinkImageFilter.h"

#if ITK_VERSION_MAJOR < 4
#define ThreadIdType int
#endif


namespace itk
{
namespace Local
{

/** \class BinShrinkImageFilter
 * \brief Reduce the size of an image by an integer factor in each
 * dimension.
 *
 * BinShrinkImageFilter reduces the size of an image by an integer factor
 * in each dimension. The algorithm implemented is a mean or box
 * filter subsample.
 *
 * The output image size in each dimension is given by:
 *
 * outputSize[j] = max( vcl_floor(inputSize[j]/shrinkFactor[j]), 1 );
 *
 * NOTE: The physical centers of the input and output will be the
 * same. Because of this, the Origin of the output may not be the same
 * as the Origin of the input.
 * Since this filter produces an image which is a different
 * resolution, origin and with different pixel spacing than its input
 * image, it needs to override several of the methods defined
 * in ProcessObject in order to properly manage the pipeline execution model.
 * In particular, this filter overrides
 * ProcessObject::GenerateInputRequestedRegion() and
 * ProcessObject::GenerateOutputInformation().
 *
 * This filter is implemented as a multithreaded filter.  It provides a
 * ThreadedGenerateData() method for its implementation.
 *
 * \ingroup GeometricTransforms Streamed
 */
template <class TInputImage, class TOutputImage>
class ITK_EXPORT BinShrinkImageFilter:
    public ShrinkImageFilter<TInputImage,TOutputImage>
{
public:
  /** Standard class typedefs. */
  typedef BinShrinkImageFilter                          Self;
  typedef ShrinkImageFilter<TInputImage,TOutputImage>   Superclass;
  typedef SmartPointer<Self>                            Pointer;
  typedef SmartPointer<const Self>                      ConstPointer;

  /** Method for creation through the object factory. */
  itkNewMacro(Self);

  /** Run-time type information (and related methods). */
  itkTypeMacro(BinShrinkImageFilter, ShrinkImageFilter);

  /** Typedef to images */
  typedef TOutputImage                                OutputImageType;
  typedef TInputImage                                 InputImageType;
  typedef typename OutputImageType::Pointer           OutputImagePointer;
  typedef typename InputImageType::Pointer            InputImagePointer;
  typedef typename InputImageType::ConstPointer       InputImageConstPointer;

  typedef typename TOutputImage::IndexType            OutputIndexType;
  typedef typename TInputImage::IndexType             InputIndexType;
  typedef typename TOutputImage::OffsetType           OutputOffsetType;

  /** Typedef to describe the output image region type. */
  typedef typename TOutputImage::RegionType OutputImageRegionType;

  /** ImageDimension enumeration. */
  itkStaticConstMacro(ImageDimension, unsigned int,
                      TInputImage::ImageDimension );
  itkStaticConstMacro(OutputImageDimension, unsigned int,
                      TOutputImage::ImageDimension );

  /** BinShrinkImageFilter needs a larger input requested region than the output
   * requested region.  As such, BinShrinkImageFilter needs to provide an
   * implementation for GenerateInputRequestedRegion() in order to inform the
   * pipeline execution model.
   * \sa ProcessObject::GenerateInputRequestedRegion() */
  virtual void GenerateInputRequestedRegion();


#ifdef ITK_USE_CONCEPT_CHECKING
  /** Begin concept checking */
  itkConceptMacro(InputConvertibleToOutputCheck,
    (Concept::Convertible<typename TInputImage::PixelType, typename TOutputImage::PixelType>));
  itkConceptMacro(SameDimensionCheck,
    (Concept::SameDimension<ImageDimension, OutputImageDimension>));
  /** End concept checking */
#endif

protected:
  BinShrinkImageFilter();
  ~BinShrinkImageFilter() {};

  /** BinShrinkImageFilter can be implemented as a multithreaded filter.
   * Therefore, this implementation provides a ThreadedGenerateData() routine
   * which is called for each processing thread. The output image data is
   * allocated automatically by the superclass prior to calling
   * ThreadedGenerateData().  ThreadedGenerateData can only write to the
   * portion of the output image specified by the parameter
   * "outputRegionForThread"
   *
   * \sa ImageToImageFilter::ThreadedGenerateData(),
   *     ImageToImageFilter::GenerateData() */
  void ThreadedGenerateData(const OutputImageRegionType& outputRegionForThread,
                            ThreadIdType threadId );

private:
  BinShrinkImageFilter(const Self&); //purposely not implemented
  void operator=(const Self&); //purposely not implemented

  OutputOffsetType ComputeOffsetIndex(void);
};

} // end namespace Local
} // end namespace itk

#ifndef ITK_MANUAL_INSTANTIATION
#include "itkBinShrinkImageFilter.txx"
#endif

#endif
