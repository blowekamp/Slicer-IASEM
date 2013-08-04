cmake_minimum_required(VERSION 2.8.8)

project(IASEMExtension)


# Common variable to extension and CLI modules
set(_EXT_HOMEPAGE "http://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/IASEM" )
set(_EXT_CATEGORY "Microscopy")
set(_EXT_CONTRIBUTORS "Bradley Lowekamp")
set(_EXT_ACKNOWLEDGEMENTS "This work could not have been done without the support of the Slicer Community and the Insight Consortium.")
set(_EXT_MAJOR_VERSION 0)
set(_EXT_MINOR_VERSION 1)
set(_EXT_PATCH_VERSION 0)
set(_EXT_LICENSE_SHORT_DESCRIPTION "Apache License 2.0" )

# Manditory
set(_EXT_NAME IASEM)

set(_EXT_ICONURL "http://raw.github.com/blowekamp/Slicer-IASEM/master/IASEM.png")
set(_EXT_DESCRIPTION "This extension is a compilation of modules which are useful for segmentation and processing of IASEM Electron Microscopy images.")
set(_EXT_SCREENSHOTURLS "http://www.slicer.org/slicerWiki/images/c/cd/IASEM-Screenshot1.png")

set(_EXT_STATUS "Experimental")


# Manditory
set(EXTENSION_NAME "${_EXT_NAME}" )
set(EXTENSION_HOMEPAGE "${_EXT_HOMEPAGE}" )
set(EXTENSION_CATEGORY "${_EXT_CATEGORY}" )

set(EXTENSION_CONTRIBUTORS "${_EXT_CONTRIBUTORS}" )
set(EXTENSION_DESCRIPTION "${EXT_DESCRIPTION}" )
set(EXTENSION_ICONURL "${_EXT_ICONURL}" )
set(EXTENSION_SCREENSHOTURLS "${_EXT_SCREENSHOTURLS}" )
set(EXTENSION_DEPENDS "")

set(EXTENSION_MAJOR_VERSION "${_EXT_MAJOR_VERSION}" )
set(EXTENSION_MINOR_VERSION "${_EXT_MINOR_VERSION}" )
set(EXTENSION_PATCH_VERSION "${_EXT_PATCH_VERSION}" )
set(EXTENSION_STATUS "${_EXT_STATUS}" )

find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

if(Slicer_USE_SimpleITK)
  # this find is needed to define SimpleITK_USE_FILE
  find_package(SimpleITK REQUIRED)

  include(${SimpleITK_USE_FILE})
else()
  message(WARNING "Slicer is not configured for SimpleITK.\nSome modules will be disabled.")
endif()

#-----------------------------------------------------------------------------
# Each module in the extension is placed in it's own directory

# standard ITK CLI module
add_subdirectory( BinShrink )

if(Slicer_USE_SimpleITK)

  #add_subdirectory( SimpleTest )
  add_subdirectory( SpacingAwareCurvatureDiffusion )

  # scripted SimpleITK Editor Effects
  add_subdirectory( DoubleThresholdEffect )
  # now included in main repository
  #add_subdirectory( WatershedFromMarker )
  add_subdirectory( BinaryWatershed )

endif()

#-----------------------------------------------------------------------------
if(BUILD_TESTING)
  add_subdirectory(Testing)
endif()

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})

