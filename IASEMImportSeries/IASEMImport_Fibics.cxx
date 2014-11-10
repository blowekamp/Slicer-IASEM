#include "IASEMImportSeries.h"

#include "itk_tiff.h"

#include "expat.h"

#include <numeric>
#include <algorithm>

#define TIFFTAG_FIBICS 51023

std::string ExtractFibicsXMLFromTiff( const std::string &fname )
{
  int value_count = 0;
  int ret = 0;
  std::string result;
  
  // Check that TIFFImageIO can read this file:
  TIFFErrorHandler save = TIFFSetWarningHandler(0);

  TIFF *tiff = TIFFOpen(fname.c_str(), "r");
  TIFFSetWarningHandler(save);

  const TIFFField *fld = TIFFFieldWithTag(tiff, TIFFTAG_FIBICS);

  if (!fld || !TIFFFieldPassCount( fld ) )
    {
    ;
    }
  else if ( TIFFFieldReadCount( fld ) == TIFF_VARIABLE2 )
    {
    uint32 cnt;
    const char *buffer;
    ret = TIFFGetField(tiff, TIFFTAG_FIBICS, &cnt, &buffer);
    value_count = cnt;
    result = buffer;
    }
  else if ( TIFFFieldReadCount( fld ) == TIFF_VARIABLE )
    {
    uint16 cnt;
    const char *buffer;
    ret = TIFFGetField(tiff, TIFFTAG_FIBICS, &cnt, &buffer);
    value_count = cnt;
    result = buffer;
    }

  if ( fld && ret == 1 )
    {
    TIFFDataType type = TIFFFieldDataType( fld );
    if ( type != TIFF_ASCII)
      {
      std::cerr << "Tag is not of type TIFF_ASCII " << type << std::endl;
      return "";
      }
    }
  else
    {
    std::cerr << "Tag " << TIFFTAG_FIBICS <<  " cannot be found." << std::endl;
    }

  if (tiff)
    {
    TIFFClose(tiff);
    }

  return result;
}

struct XMLParseData
{
  XMLParseData(void) : depth(0) {}
  ~XMLParseData(void) {}
  int depth;
  std::vector<std::string> elements;
  std::vector<std::string> data;
  FibicsData *fd;
};

bool is_equal_elements(const std::vector<std::string> &elements_v, const char **elements_c)
{
  size_t i = 0;

  while (elements_c[i])
    {
    ++i;
    }

  std::vector<std::string>::const_reverse_iterator viter = elements_v.rbegin();

  if (elements_v.size()<i)
    {
    return false;
    }

  while(i--!=0)
    {
    if(*viter!=elements_c[i])
      {
      return false;
      }
    ++viter;
    }
  return true;
}

void ProcessData( const XMLParseData &pd )
{
  const char *pathUx[] = {"Scan","Ux", 0};
  const char *pathUy[] = {"Scan","Uy", 0};
  const char *pathVx[] = {"Scan","Vx", 0};
  const char *pathVy[] = {"Scan","Vy", 0};
  const char *pathZPos[] = {"ATLAS3D", "Slice", "ZPos", 0};
  const char *pathBoundingBox_Left[] = {"Image", "BoundingBox.Left", 0};
  const char *pathBoundingBox_Right[] = {"Image", "BoundingBox.Right", 0};
  const char *pathBoundingBox_Top[] = {"Image", "BoundingBox.Top", 0};
  const char *pathBoundingBox_Bottom[] = {"Image", "BoundingBox.Bottom", 0};



  if (is_equal_elements(pd.elements, pathUx))
    {
    pd.fd->Ux = atof(pd.data.back().c_str());
    }
  if (is_equal_elements(pd.elements, pathUy))
    {
    pd.fd->Uy = atof(pd.data.back().c_str());
    }

  if (is_equal_elements(pd.elements, pathVx))
    {
    pd.fd->Vx = atof(pd.data.back().c_str());
    }
  if (is_equal_elements(pd.elements, pathVy))
    {
    pd.fd->Vy = atof(pd.data.back().c_str());
    }

  if (is_equal_elements(pd.elements, pathZPos))
    {
    pd.fd->ZPos = atof(pd.data.back().c_str());
    }

  if (is_equal_elements(pd.elements, pathBoundingBox_Left))
    {
    pd.fd->BoundingBox_Left = atoi(pd.data.back().c_str());
    }
  if (is_equal_elements(pd.elements, pathBoundingBox_Right))
    {
    pd.fd->BoundingBox_Right = atoi(pd.data.back().c_str());
    }
  if (is_equal_elements(pd.elements, pathBoundingBox_Top))
    {
    pd.fd->BoundingBox_Top = atoi(pd.data.back().c_str());
    }
  if (is_equal_elements(pd.elements, pathBoundingBox_Bottom))
    {
    pd.fd->BoundingBox_Bottom = atoi(pd.data.back().c_str());
    }

}


namespace
{
void start_element(void *data, const XML_Char *el, const XML_Char **itkNotUsed(attr) )
{
  assert(data);
  XMLParseData &pd = *reinterpret_cast<XMLParseData*>(data);
  pd.elements.push_back(std::string(el));
  pd.data.push_back(std::string());
  ++pd.depth;
}

void end_element(void *data, const XML_Char *itkNotUsed(el))
{
  assert(data);
  XMLParseData &pd = *reinterpret_cast<XMLParseData*>(data);

  ProcessData(pd);

  pd.elements.pop_back();
  pd.data.pop_back();
  --pd.depth;
}

void data(void *data, const XML_Char *s, int len)
{
  assert(data);
  XMLParseData &pd = *reinterpret_cast<XMLParseData*>(data);

  pd.data.back().append(s,len);
}

}



FibicsData ExtractFibicsData( const char*xml, int len )
{
  if (len==0)
    {
    len=strlen(xml);
    }

  FibicsData fd;
  XMLParseData pd;
  pd.fd = &fd;
  
  XML_Parser parser = XML_ParserCreate(NULL);

  if (!parser)
    return fd;

  XML_SetElementHandler(parser, start_element, end_element);

  XML_SetCharacterDataHandler(parser, data);

  XML_SetUserData(parser, &pd);

  if (XML_Parse(parser,xml,len,1) == 0 )
    {
    std::cerr << "Error: " << XML_ErrorString(XML_GetErrorCode(parser)) << std::endl;
    }

  XML_ParserFree(parser);

  return *(pd.fd);
}



void ExtractFibicsInfo( const std::vector<std::string> &sliceList,
                        itk::Vector<double, 3> &spacing,
                        itk::ImageRegion<2> &reduced_bb)
{
  std::vector<FibicsData> fibicsDataArray(sliceList.size());


  for( unsigned int i = 0; i <  sliceList.size(); ++i )
    {

    const std::string fibicsXML = ExtractFibicsXMLFromTiff(sliceList[i]);
    if (fibicsXML.size())
      {
      fibicsDataArray[i] = ExtractFibicsData(fibicsXML.c_str());
      }
    }

  //
  // Compute union of bounding boxes
  //
  std::vector<FibicsData>::const_iterator fd_iter = fibicsDataArray.begin();
  reduced_bb.SetIndex(0, fd_iter->BoundingBox_Left);
  reduced_bb.SetIndex(1, fd_iter->BoundingBox_Top);
  if ( fd_iter->BoundingBox_Right > fd_iter->BoundingBox_Left)
    reduced_bb.SetSize(0, fd_iter->BoundingBox_Right-fd_iter->BoundingBox_Left);
  if (fd_iter->BoundingBox_Bottom > fd_iter->BoundingBox_Top)
    reduced_bb.SetSize(1, fd_iter->BoundingBox_Bottom-fd_iter->BoundingBox_Top);

  while( ++fd_iter != fibicsDataArray.end() )
    {
    const itk::Index<2> start = reduced_bb.GetIndex();
    itk::Index<2> upper = reduced_bb.GetUpperIndex();

    reduced_bb.SetIndex(0, std::min<itk::IndexValueType>( start[0], fd_iter->BoundingBox_Left ));
    reduced_bb.SetIndex(1, std::min<itk::IndexValueType>( start[1], fd_iter->BoundingBox_Top ));

    if ( fd_iter->BoundingBox_Right > fd_iter->BoundingBox_Left)
      {
      upper[0] = std::max<itk::IndexValueType>( upper[0], fd_iter->BoundingBox_Right-1 );
      }
    if (fd_iter->BoundingBox_Bottom > fd_iter->BoundingBox_Top)
      {
      upper[1] = std::max<itk::IndexValueType>( upper[1], fd_iter->BoundingBox_Bottom-1 );
      }
    reduced_bb.SetUpperIndex(upper);
    }

  // Compute XY spacing average
  fd_iter = fibicsDataArray.begin();
  spacing[0] = 0.0;
  spacing[1] = 0.0;
  while( ++fd_iter != fibicsDataArray.end() )
    {
    const double U = std::sqrt(fd_iter->Ux*fd_iter->Ux+fd_iter->Uy*fd_iter->Uy);
    spacing[0] += U;
    const double V = std::sqrt(fd_iter->Vx*fd_iter->Vx+fd_iter->Vy*fd_iter->Vy);
    spacing[1] += V;
    }
  spacing[0] /= fibicsDataArray.size();
  spacing[1] /= fibicsDataArray.size();

  // compute z-Pos difference for spacing
  fd_iter = fibicsDataArray.begin();
  std::vector<double> z_array;
  z_array.reserve(fibicsDataArray.size());
  while( ++fd_iter != fibicsDataArray.end() )
    {
    z_array.push_back(fd_iter->ZPos);
    }
  std::adjacent_difference(z_array.begin(), z_array.end(), z_array.begin());

  // remove first element which is not a difference.
  std::swap(z_array.front(), z_array.back());
  z_array.pop_back();

  // compute mean just FYI
  double z_mean = std::accumulate(z_array.begin(), z_array.end(), 0.0)/z_array.size();

  // compute z-spacing median
  std::sort(z_array.begin(), z_array.end());
  spacing[2] = z_array[z_array.size()/2];
  if (z_array.size()%2==0)
    {
    //odd
    spacing[2] = (spacing[2] + z_array[z_array.size()/2-1])/2.0;
    }

  // microns to nm
  spacing[0] *= 1000;
  spacing[1] *= 1000;
  spacing[2] *= 1000;

  std::cout << "Fibics XML Z Median: " << spacing[2] << std::endl;
  std::cout << "Fibics XML Z Mean: " << z_mean << std::endl;
  std::cout << "Fibics XML BB: " << reduced_bb.GetIndex(0)
            << " " << reduced_bb.GetIndex(1)
            << " " << reduced_bb.GetUpperIndex()[0]
            << " " << reduced_bb.GetUpperIndex()[1]
            << std::endl;
}

