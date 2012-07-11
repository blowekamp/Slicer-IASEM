
#include "itkPluginUtilities.h"
#include "SimpleITK.h"
#include "sitkImageOperators.h"

#include "NucleusClosingCLP.h"
#include <algorithm>

namespace sitk = itk::simple;

int main( int argc, char * argv[] )
{
  PARSE_ARGS;

  try
    {

    if ( pad >= radius )
      {
      sitkExceptionMacro( "Pad must be less than radius!" );
      }

    sitk::Image img = sitk::ReadImage( inputVolume );

    // extract just the label of interest
    sitk::Image l = sitk::BinaryThreshold( img, labelID, labelID, 1, 0 );

    // The grayscale erode adn dilate are faster then the binary
    sitk::Image temp = sitk::BinaryDilate( l, radius );
    temp = sitk::BinaryFillhole( temp );
    temp = sitk::BinaryErode( temp, radius - pad );

    sitk::Image outter = sitk::BinaryContourImageFilter().FullyConnectedOn().Execute(temp);
    sitk::Image inner = l | sitk::BinaryErode( temp, radius+pad );

    sitk::WriteImage( sitk::Cast( 2*inner+outter, sitk::sitkUInt16), outputVolume );

    }

  catch( itk::ExceptionObject & excep )
    {
    std::cerr << argv[0] << ": exception caught !" << std::endl;
    std::cerr << excep << std::endl;
    return EXIT_FAILURE;
    }
  return EXIT_SUCCESS;
}
