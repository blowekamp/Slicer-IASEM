#ifndef __IASEMImportSeries_h__
#define __IASEMImportSeries_h__
#include "itkAffineTransform.h"
#include "itkImageRegion.h"
#include <string>


typedef std::vector<  itk::Transform< double, 2, 2 >::Pointer > TransformListType;



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

class FibicsData
{
  // note: class used default copy constructor, assignment operator
  // and destructor
public:
  FibicsData()
    : Ux(0.0), Uy(0.0), Vx(0.0), Vy(0.1),
      ZPos(0.0),
      BoundingBox_Left(0), BoundingBox_Right(0), BoundingBox_Top(0), BoundingBox_Bottom(0)
    {}

  // Docs From: Schema FibicsInfo_1_0.xsd
  // The version attribute is the version of the fibics information
  // data file.  As of 2012-11-12, the current version is 1.0.

  // A single Ux element will always exist.  The Ux element contains a
  // floating point number that is the X-component of the pixel U-unit
  // vector.  That is, moving one pixel in the row (width) direction
  // will shift you Ux in the world X direction.
  double Ux;
  double Uy;
  double Vx;
  double Vy;

  // The NominalZPos contains the Z position of this image in the
  // image stack, calculated from the progress in the FIB milling
  // operation (FIBLineSpacing x FIBLineNo in pause-and-image mode).
  // If 3D tracking was used, ZPos should be used as it includes the
  // drift correction value.  The Z direction for NominalZPos is into
  // the sample face - that is, an image with a higher Z value is
  // collected later than an image with a lower Z value.
  double ZPos;

  // A single BoundingBox.Left element may be present.  The
  // BoundingBox.Left element defines the left-most column of pixels
  // that contains valid information.  BoundingBox.Left will be &gt;=
  // 0 and BoundingBox.Left will be &lt;= BoundingBox.Right.  Pixel
  // data in columns less than BoundingBox.Left does not need to be
  // read.
  size_t BoundingBox_Left;
  size_t BoundingBox_Right;
  size_t BoundingBox_Top;
  size_t BoundingBox_Bottom;

};

std::string ExtractFibicsXMLFromTiff( const std::string &fname );
FibicsData ExtractFibicsData( const char*xml, int len = 0 );
void ExtractFibicsInfo( const std::vector<std::string> &sliceList,
                        itk::Vector<double, 3> &spacing,
                        itk::ImageRegion<2> &reduced_bb);

TransformListType ReadXGTransform( const std::string &xgFileName );

itk::ImageRegion<2> ComputeBoundingBox( const std::string &fname, bool flip=true );

#endif // __IASEMImportSeries_h__
