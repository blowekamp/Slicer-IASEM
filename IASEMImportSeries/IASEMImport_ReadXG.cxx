#include "IASEMImportSeries.h"

#include <fstream>

// ITK headers
#include "itkArray.h"

TransformListType ReadXGTransform( const std::string &xgFileName )
{
  std::ifstream fin( xgFileName.c_str(), std::ios_base::in );

  typedef itk::AffineTransform< double,  2> TransformType;

  // initialize transformation array
  TransformListType sliceTransforms;

  // note: this is not a very robust reading block
  itk::Array<double> line(6);
  while ( !fin.eof() )
    {

    // read in line of 6 real numbers, the first 4 are a matrix in
    // row-major order, then 2 translation vectors
    fin >> line[0] >> line[1] >> line[2] >> line[3] >> line[4] >> line[5];

    if ( fin.good() )
      {
      // successfully read in the line, set the transform parameters
      TransformType::Pointer t = TransformType::New();
      TransformType::Pointer out = TransformType::New();
      t->SetParameters( line );
      t->GetInverse(out);
      sliceTransforms.push_back( out.GetPointer() );

      }
    else if ( fin.fail()  && !fin.eof() )
      {
      //  problem reading one line, clear it and try to keep going
      std::cerr << "fail in reading line " << fin.eof() << std::endl;
      fin.clear();
      }
    if ( fin.bad() )
      {
      // file is now corupt, give up and return nothing.
      std::cerr << "unexpected bad file state" << std::endl;
      return TransformListType();
      }
    }

  return sliceTransforms;


}
