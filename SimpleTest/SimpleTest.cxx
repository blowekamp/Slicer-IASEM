#include "itkImageFileWriter.h"

#include "itkSmoothingRecursiveGaussianImageFilter.h"

#include "itkPluginUtilities.h"
#include "SimpleITK.h"

#include "SimpleTestCLP.h"

namespace sitk = itk::simple;

int main( int argc, char * argv[] )
{
  PARSE_ARGS;

  try
    {

    sitk::Image img = sitk::ReadImage( inputVolume );
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
