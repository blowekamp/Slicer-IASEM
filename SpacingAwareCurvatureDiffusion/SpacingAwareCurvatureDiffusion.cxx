
#include "itkPluginUtilities.h"
#include "SimpleITK.h"

#include "SpacingAwareCurvatureDiffusionCLP.h"

#include <algorithm>

namespace sitk = itk::simple;

int main( int argc, char * argv[] )
{
  PARSE_ARGS;

  try
    {

    sitk::Image img = sitk::ReadImage( inputVolume );
    sitk::PixelIDValueType inputPixel = img.GetPixelIDValue();
    img = sitk::Cast( img, sitk::sitkFloat32 );

    std::vector<double> spacing = img.GetSpacing();
    double minSpacing = *std::min_element( spacing.begin(), spacing.end() );

    sitk::CurvatureAnisotropicDiffusionImageFilter filter;
    filter.SetConductanceParameter( conductance  );
    filter.SetNumberOfIterations( numberOfIterations );
    filter.SetTimeStep( timeStep * minSpacing );
    img = filter.Execute( img );

    // cast back to the input image type
    img = sitk::Cast( img, inputPixel );

    sitk::WriteImage( img, outputVolume );

    }

  catch( itk::ExceptionObject & excep )
    {
    std::cerr << argv[0] << ": exception caught !" << std::endl;
    std::cerr << excep << std::endl;
    return EXIT_FAILURE;
    }
  return EXIT_SUCCESS;
}
