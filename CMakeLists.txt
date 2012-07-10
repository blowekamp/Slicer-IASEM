cmake_minimum_required(VERSION 2.8.8)

# Manditory
set(_EXT_NAME IASEM) # Do not use 'project()'
set(_EXT_HOMEPAGE "http://www.slicer.org/slicerWiki/index.php/Slicer4:Developers:Projects:QtSlicer/Tutorials/ExtensionWriting")
set(_EXT_CATEGORY "Microscopy")

# Optional
set(_EXT_CONTRIBUTORS "Bradley Lowekamp")
set(_EXT_ICONURL "http://viewvc.slicer.org/viewvc.cgi/Slicer4/trunk/Extensions/Testing/IASEM/IASEM.png?revision=19437&view=co")
set(_EXT_DESCRIPTION "This extension is a compilation of modules which are useful for IASEM Electron Microscopy.")
set(_EXT_SCREENSHOTURLS "http://wiki.slicer.org/slicerWiki/images/a/ab/Slicer-r19441-IASEM-screenshot.png")

# Legacy?
set(_EXT_ACKNOWLEDGEMENTS "This work could not have been done without the support of the Slicer Community and the Insight Consortium.")

set(_EXT_MAJOR_VERSION 0)
set(_EXT_MINOR_VERSION 1)
set(_EXT_PATCH_VERSION 0)
set(_EXT_STATUS "Experimental")

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  # Manditory
  set(EXTENSION_NAME ${_EXT_NAME} ) # Do not use 'project()'
  set(EXTENSION_HOMEPAGE ${_EXT_HOMEPAGE} )
  set(EXTENSION_CATEGORY ${_EXT_CATEGORY} )

  # Optional
  set(EXTENSION_CONTRIBUTORS ${_EXT_CONTRIBUTORS} )
  set(EXTENSION_ICONURL ${_EXT_ICONURL} )
  set(EXTENSION_DESCRIPTION ${EXT_DESCRIPTION} )
  set(EXTENSION_SCREENSHOTURLS ${_EXT_SCREENSHOTURLS} )

  # Legacy?
  set(EXTENSION_ACKNOWLEDGEMENTS ${_EXT_ACKNOWLEDGEMENTS} )

  set(EXTENSION_MAJOR_VERSION ${_EXT_MAJOR_VERSION} )
  set(EXTENSION_MINOR_VERSION ${_EXT_MINOR_VERSION} )
  set(EXTENSION_PATCH_VERSION ${_EXT_PATCH_VERSION} )
  set(EXTENSION_STATUS ${_EXT_STATUS} )
endif()

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  find_package(Slicer REQUIRED)
  include(${Slicer_USE_FILE})
endif()


if(Slicer_USE_SimpleITK)

  # this find is needed to define SimpleITK_USE_FILE
  find_package(SimpleITK REQUIRED)

  include(${SimpleITK_USE_FILE})
else()
  message(WARNING "Slicer is not configured for SimpleITK.\nSome modules will be disabled.")
endif()

#-----------------------------------------------------------------------------
# Each module in the extension is placed in it's own directory
add_subdirectory( BinShrink )

add_subdirectory( DoubleThresholdEffect )
add_subdirectory( WatershedFromMarker )
add_subdirectory( BinaryWatershed )

if(Slicer_USE_SimpleITK)
  add_subdirectory( SimpleTest )
  add_subdirectory( SpacingAwareCurvatureDiffusion )

endif()

#-----------------------------------------------------------------------------
if(BUILD_TESTING)
  add_subdirectory(Testing)
endif()

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  include(${Slicer_EXTENSION_CPACK})
endif()

