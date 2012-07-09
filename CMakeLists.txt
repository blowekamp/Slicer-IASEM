cmake_minimum_required(VERSION 2.8.8)

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  # Manditory
  set(EXTENSION_NAME IASEM) # Do not use 'project()'
  set(EXTENSION_HOMEPAGE "http://www.slicer.org/slicerWiki/index.php/Slicer4:Developers:Projects:QtSlicer/Tutorials/ExtensionWriting")
  set(EXTENSION_CATEGORY "Microscopy")

  # Optional
  set(EXTENSION_CONTRIBUTORS "Bradley Lowekamp")
  set(EXTENSION_ICONURL "http://viewvc.slicer.org/viewvc.cgi/Slicer4/trunk/Extensions/Testing/IASEM/IASEM.png?revision=19437&view=co")
  set(EXTENSION_DESCRIPTION "This extension is a compilation of modules which are useful for IASEM Electron Microscopy.")
  set(EXTENSION_SCREENSHOTURLS "http://wiki.slicer.org/slicerWiki/images/a/ab/Slicer-r19441-IASEM-screenshot.png")

  # Legacy?
  set(EXTENSION_ACKNOWLEDGEMENTS "This work could not have been done without the support of the Slicer Community and the Insight Consortium.")

  set(EXTENSION_MAJOR_VERSION 0)
  set(EXTENSION_MINOR_VERSION 1)
  set(EXTENSION_PATCH_VERSION 0)
  set(EXTENSION_STATUS "Experimental")
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

