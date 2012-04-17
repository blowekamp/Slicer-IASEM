/*=========================================================================

  Program:   Insight Segmentation & Registration Toolkit
  Module:    $RCSfile: itkBinShrinkImageFilter.txx,v $
  Language:  C++
  Date:      $Date$
  Version:   $Revision$

  Copyright (c) Insight Software Consortium. All rights reserved.
  See ITKCopyright.txt or http://www.itk.org/HTML/Copyright.htm for details.

  Portions of this code are covered under the VTK copyright.
  See VTKCopyright.txt or http://www.kitware.com/VTKCopyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notices for more information.

=========================================================================*/
#ifndef __itkBinShrinkImageFilter_txx
#define __itkBinShrinkImageFilter_txx

#include "itkBinShrinkImageFilter.h"
#include "itkImageRegionIteratorWithIndex.h"
#include "itkConstShapedNeighborhoodIterator.h"
#include "itkProgressReporter.h"

namespace itk
{
namespace Local
{

/**
 *
 */
template <class TInputImage, class TOutputImage>
BinShrinkImageFilter<TInputImage,TOutputImage>
::BinShrinkImageFilter()
{
}


/**
 *
 */
template <class TInputImage, class TOutputImage>
void
BinShrinkImageFilter<TInputImage,TOutputImage>
::ThreadedGenerateData(const OutputImageRegionType& outputRegionForThread,
                       ThreadIdType threadId)
{
  itkDebugMacro(<<"Actually executing");

  // Get the input and output pointers
  InputImageConstPointer  inputPtr = this->GetInput();
  OutputImagePointer      outputPtr = this->GetOutput();

  typedef typename NumericTraits<typename TInputImage::PixelType>::RealType AccumulatePixelType;

  // Define/declare an iterator that will walk the output region for this
  // thread.
  typedef ImageRegionIteratorWithIndex<TOutputImage> OutputIterator;
  OutputIterator outIt(outputPtr, outputRegionForThread);


  // Define a few indices that will be used to transform from an input pixel
  // to an output pixel
  OutputIndexType   outputIndex;
  InputIndexType    inputIndex;
  OutputOffsetType  offsetIndex  = this->ComputeOffsetIndex();

  typedef ConstShapedNeighborhoodIterator< TInputImage > ConstNeighborhoodIteratorType;
  typename ConstNeighborhoodIteratorType::RadiusType radius;
  typedef typename ConstNeighborhoodIteratorType::RadiusType::SizeValueType RadiusValueType;
  for (unsigned int i=0; i < TInputImage::ImageDimension; i++)
    {
    radius[i] = Math::Ceil<RadiusValueType>( this->GetShrinkFactors()[i]*0.5 - 0.5);
    }

  ConstNeighborhoodIteratorType inputIt( radius, inputPtr,
                                         inputPtr->GetRequestedRegion() );


  // Set up shaped neighbor hood by defining the offsets
  OutputOffsetType negativeOffset, positiveOffset, iOffset;
  typedef typename OutputOffsetType::OffsetValueType OffsetValueType;
  for ( unsigned int i=0; i < TInputImage::ImageDimension; i++)
    {
    negativeOffset[i] = -Math::Ceil<OffsetValueType>( this->GetShrinkFactors()[i]*0.5 - 0.5);
    positiveOffset[i] =  Math::Floor<OffsetValueType>( this->GetShrinkFactors()[i]*0.5 - 0.5);
    }

  iOffset = negativeOffset;
  while (iOffset[TInputImage::ImageDimension-1] <= positiveOffset[TInputImage::ImageDimension-1])
    {
    inputIt.ActivateOffset( iOffset );

    ++iOffset[0];

    for (unsigned int i=0; i < TInputImage::ImageDimension - 1; i++)
      {
      if (iOffset[i] > positiveOffset[i])
        {
        iOffset[i] = negativeOffset[i];
        ++iOffset[i+1];
        }
      }
    }


  // convert the shrink factor for convenient multiplication
  typename TOutputImage::SizeType  factorSize;
  for (unsigned int i=0; i < TInputImage::ImageDimension; i++)
    {
    factorSize[i] = this->GetShrinkFactors()[i];
    }


  bool degeneratelySmall = false;
  const typename TInputImage::SizeType &inputSize = inputPtr->GetLargestPossibleRegion().GetSize();
  for (unsigned int i=0; i < TInputImage::ImageDimension; i++)
    {
    // the interator neighborhood will fit unless the image was
    // degenerately small, ie the followign is true
    if ( inputSize[i] < this->GetShrinkFactors()[i] )
      {
      degeneratelySmall = true;
      break;
      }
    }
  /*
  // we don't use a face algorithm since we know the neighborhood must
  // fit unless the input image was degeneratly small
  if ( degeneratelySmall )
    {
    inputIt.NeedToUseBoundaryConditionOn();
    }
  else
    {
    inputIt.NeedToUseBoundaryConditionOff();
    }
  */

  // support progress methods/callbacks
  ProgressReporter progress(this, threadId, outputRegionForThread.GetNumberOfPixels());

  while ( !outIt.IsAtEnd() )
    {
    // determine the index and physical location of the output pixel
    outputIndex = outIt.GetIndex();

    // an optimized version of
    // outputPtr->TransformIndexToPhysicalPoint(outputIndex, tempPoint);
    // inputPtr->TransformPhysicalPointToIndex(tempPoint, inputIndex);
    // but without the rounding and precision issues
    inputIndex = outputIndex * factorSize + offsetIndex;

    // Set the iterator at the desired location
    inputIt.SetLocation( inputIndex );


    AccumulatePixelType sum = NumericTraits<AccumulatePixelType>::Zero;
    // Walk the neighborhood

    typename ConstNeighborhoodIteratorType::ConstIterator ci = inputIt.Begin();

    for (ci.GoToBegin(); !ci.IsAtEnd(); ++ci)
      {
      sum += AccumulatePixelType( ci.Get() );
      }
    // this statement is made to work with RGB pixel types
    sum = sum * (1.0 / double( inputIt.GetActiveIndexListSize() ) );

    // set the mean value to the output image
    outIt.Set( sum );
    ++outIt;

    progress.CompletedPixel();
    }
}


/**
 *
 */
template <class TInputImage, class TOutputImage>
void
BinShrinkImageFilter<TInputImage,TOutputImage>
::GenerateInputRequestedRegion()
{
  // call the superclass' implementation of this method
  Superclass::GenerateInputRequestedRegion();

  // get pointers to the input and output
  InputImagePointer  inputPtr = const_cast<TInputImage *> (this->GetInput());
  OutputImagePointer outputPtr = this->GetOutput();

  if ( !inputPtr || !outputPtr )
    {
    return;
    }

  // Compute the input requested region (size and start index)
  // Use the image transformations to insure an input requested region
  // that will provide the proper range
  unsigned int i;
  const typename TOutputImage::SizeType& outputRequestedRegionSize
    = outputPtr->GetRequestedRegion().GetSize();
  const typename TOutputImage::IndexType& outputRequestedRegionStartIndex
    = outputPtr->GetRequestedRegion().GetIndex();


  typename TInputImage::IndexType  inputIndex0,  inputIndex1;
  typename TInputImage::SizeType   inputSize;

  // convert the shrink factor for convenient multiplication
  typename TOutputImage::SizeType  factorSize;
  for (unsigned int i=0; i < TInputImage::ImageDimension; i++)
    {
    factorSize[i] = this->GetShrinkFactors()[i];
    }

  OutputOffsetType  offsetIndex  = this->ComputeOffsetIndex();


  typename TInputImage::OffsetType negativeOffset, positiveOffset;
  typedef typename TInputImage::OffsetType::OffsetValueType OffsetValueType;
  for ( i=0; i < TInputImage::ImageDimension; i++)
    {
    negativeOffset[i] = -Math::Ceil<OffsetValueType>( this->GetShrinkFactors()[i]*0.5 - 0.5);
    positiveOffset[i] =  Math::Floor<OffsetValueType>( this->GetShrinkFactors()[i]*0.5 - 0.5);
    }

  for ( i=0; i < TInputImage::ImageDimension; i++)
    {
    inputIndex0[i] = outputRequestedRegionStartIndex[i]*factorSize[i] + offsetIndex[i] + negativeOffset[i];
    inputIndex1[i] = (outputRequestedRegionStartIndex[i]+outputRequestedRegionSize[i]-1)*factorSize[i] + offsetIndex[i] + positiveOffset[i];

    inputSize[i] = inputIndex1[i] - inputIndex0[i] + 1;
    }


  typename TInputImage::RegionType inputRequestedRegion;
  inputRequestedRegion.SetIndex( inputIndex0 );
  inputRequestedRegion.SetSize( inputSize );


  inputRequestedRegion.Crop( inputPtr->GetLargestPossibleRegion() );

  inputPtr->SetRequestedRegion( inputRequestedRegion );
}


/**
 *
 */
template <class TInputImage, class TOutputImage>
typename BinShrinkImageFilter<TInputImage,TOutputImage>::OutputOffsetType
BinShrinkImageFilter<TInputImage,TOutputImage>
::ComputeOffsetIndex(void)
{
  // get pointers to the input and output
  InputImageConstPointer inputPtr  = this->GetInput();
  OutputImagePointer     outputPtr = this->GetOutput();

  assert( inputPtr && outputPtr );

  OutputIndexType           outputIndex;
  InputIndexType            inputIndex;
  OutputOffsetType          offsetIndex;

  typename TOutputImage::PointType tempPoint;


  // use this index to compute the offset everywhere in this class
  outputIndex = outputPtr->GetLargestPossibleRegion().GetIndex();
  inputIndex = inputPtr->GetLargestPossibleRegion().GetIndex();

  // We wish to perform the following mapping of outputIndex to
  // inputIndex on all points in our region
  outputPtr->TransformIndexToPhysicalPoint( outputIndex, tempPoint );
  inputPtr->TransformPhysicalPointToIndex( tempPoint, inputIndex );

  // Given that the size is scaled by a constant factor eq:
  // inputIndex = outputIndex * factorSize
  // is equivalent up to a fixed offset which we now compute
  for ( unsigned int i=0; i < TInputImage::ImageDimension; i++ )
    {
    offsetIndex[i] = inputIndex[i] - outputIndex[i]*this->GetShrinkFactors()[i];
    }

  return offsetIndex;
}

} // end namespace Local
} // end namespace itk

#endif
