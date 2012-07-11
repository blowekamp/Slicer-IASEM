
#include "itkPluginUtilities.h"
#include "SimpleITK.h"
#include "sitkImageOperators.h"

#include "NucleusClosingCLP.h"
#include <algorithm>

namespace sitk = itk::simple;

namespace
{

void UpdateProgress( ModuleProcessInformation * MPI, const char* message, float progress = 0.0 )
{
  if( MPI )
    {
    strncpy(MPI->ProgressMessage, message, 1023);

    if( progress != 0.0 )
      {
      MPI->Progress = progress;
      }

    if (MPI->ProgressCallbackFunction
        && MPI->ProgressCallbackClientData)
      {
      (*(MPI->ProgressCallbackFunction))(MPI->ProgressCallbackClientData);
      }
    if (MPI->Abort)
      {
      sitkExceptionMacro( "Aborted!" );
      }
    }
}

} // end namespace

int main( int argc, char * argv[] )
{
  PARSE_ARGS;

  try
    {

    if ( pad >= radius )
      {
      sitkExceptionMacro( "Pad must be less than radius!" );
      }

    UpdateProgress( CLPProcessInformation, "Reading Volume..." );

    sitk::Image img = sitk::ReadImage( inputVolume );

    // extract just the label of interest
    UpdateProgress( CLPProcessInformation, "Extracting label...", 0.01 );
    sitk::Image l = sitk::BinaryThreshold( img, labelID, labelID, 1, 0 );


    // The grayscale erode adn dilate are faster then the binary
    UpdateProgress( CLPProcessInformation, "Dilating...", 0.1 );
    sitk::Image temp = sitk::BinaryDilate( l, radius );
    UpdateProgress( CLPProcessInformation, "Filling holes...", 0.3 );
    temp = sitk::BinaryFillhole( temp );
    UpdateProgress( CLPProcessInformation, "Eroding...", 0.4 );
    temp = sitk::BinaryErode( temp, radius - pad );

    UpdateProgress( CLPProcessInformation, "Contour...", 0.6 );
    sitk::Image outter = sitk::BinaryContourImageFilter().FullyConnectedOn().Execute(temp);
    UpdateProgress( CLPProcessInformation, "2nd Erode...", 0.7 );
    sitk::Image inner = sitk::BinaryErode(l, 1) | sitk::BinaryErode( temp, radius+pad );

    UpdateProgress( CLPProcessInformation, "Writing Volume...", 0.9 );
    sitk::WriteImage( sitk::Cast( 2*inner+outter, sitk::sitkUInt16), outputVolume );
    UpdateProgress( CLPProcessInformation, "Done", 1.0 );

    }

  catch( itk::ExceptionObject & excep )
    {
    std::cerr << argv[0] << ": exception caught !" << std::endl;
    std::cerr << excep << std::endl;
    return EXIT_FAILURE;
    }
  return EXIT_SUCCESS;
}
