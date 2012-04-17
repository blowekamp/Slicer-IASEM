#-----------------------------------------------------------------------------
cmake_minimum_required(VERSION 2.8.4)
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# See http://cmake.org/cmake/help/cmake-2-8-docs.html#section_Policies for details
#-----------------------------------------------------------------------------
if(POLICY CMP0017)
  cmake_policy(SET CMP0017 OLD)
endif()

#-----------------------------------------------------------------------------
# Module name
#   - Usually identique to the directory name)
#   - You shouldn't call 'project(...)'. See SlicerConfig.cmake for more details.
#-----------------------------------------------------------------------------
set(EXTENSION_NAME IASEM)

#-----------------------------------------------------------------------------
# Extension metadata
#-----------------------------------------------------------------------------
set(EXTENSION_HOMEPAGE "http://www.slicer.org/slicerWiki/index.php/Slicer4:Developers:Projects:QtSlicer/Tutorials/ExtensionWriting")
set(EXTENSION_CATEGORY "Microscopy")
set(EXTENSION_ICONURL "http://viewvc.slicer.org/viewvc.cgi/Slicer4/trunk/Extensions/Testing/IASEM/IASEM.png?revision=19437&view=co")
set(EXTENSION_STATUS "Experimental")
set(EXTENSION_CONTRIBUTORS "Bradley Lowekamp")
set(EXTENSION_DESCRIPTION "This extension is a compilation of modules which are useful for IASEM Electron Microscopy.")
set(EXTENSION_SCREENSHOTURLS "http://wiki.slicer.org/slicerWiki/images/a/ab/Slicer-r19441-IASEM-screenshot.png http://wiki.slicer.org/slicerWiki/images/1/1e/Slicer-r19441-IASEM-screenshot-2.png")
set(EXTENSION_ACKNOWLEDGEMENTS "This work could not have been done without the support of the Slicer Community and the Insight Consortium.")
set(EXTENSION_MAJOR_VERSION 0)
set(EXTENSION_MINOR_VERSION 1)
set(EXTENSION_PATCH_VERSION 0)

# Set Module metadata to default to be the same as the extension
#-----------------------------------------------------------------------------
set(MODULE_HOMEPAGE "${EXTENSION_HOMEPAGE}" )
set(MODULE_CATEGORY "${EXTENSION_CATEGORY}" )
set(MODULE_ICONURL "${EXTENSION_ICONURL}")
set(MODULE_STATUS "${EXTENSION_STATUS}")
set(MODULE_CONTRIBUTORS "${EXTENSION_CONTRIBUTORS}")
set(MODULE_DESCRIPTION "${EXTENSION_DESCRIPTION}")
set(MODULE_SCREENSHOTURLS "${EXTENSION_SCREENSHOTURLS}")
set(MODULE_ACKNOWLEDGEMENTS "${EXTENSION_ACKNOWLEDGEMENTS}")
set(MODULE_MAJOR_VERSION "${EXTENSION_MAJOR_VERSION}")
set(MODULE_MINOR_VERSION "${EXTENSION_MINOR_VERSION}")
set(MODULE_PATCH_VERSION "${EXTENSION_PATCH_VERSION}")

#-----------------------------------------------------------------------------
# Prerequisites
#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  find_package(Slicer REQUIRED)

  # Additional C/CXX flags - Should be defined before including Slicer_USE_FILE
  set(ADDITIONAL_C_FLAGS "" CACHE STRING "Additional ${EXTENSION_NAME} C Flags")
  set(ADDITIONAL_CXX_FLAGS "" CACHE STRING "Additional ${EXTENSION_NAME} CXX Flags")

  include(${Slicer_USE_FILE})

  set(EXTENSION_DEPENDS NA) # Specified as a space separated list or 'NA' if any
  set(EXTENSION_LICENSE_FILE ${Slicer_LICENSE_FILE})
  set(EXTENSION_README_FILE ${Slicer_README_FILE})
  set(EXTENSION_LICENSE_SHORT_DESCRIPTION ${Slicer_LICENSE_SHORT_DESCRIPTION})

  include(SlicerEnableExtensionTesting)

  if(Slicer_USE_SimpleITK)
    find_package(SimpleITK REQUIRED)
    include(${SimpleITK_USE_FILE})
  else()
    message( WARNING "Slicer is not configured for SimpleITK.\n Some module will be disabled." )
  endif()



endif()

# Add module sub libraries
#add_subdirectory(Logic)

set(cli_module_export_directive "Q_SLICER_QTMODULES_LOADABLEEXTENSIONTEMPLATE_EXPORT")

# Additional includes
set(cli_module_include_directories
  )

# Additional source files
set(cli_module_SRCS
  )

# Additional Target libraries
set(cli_module_target_libraries
  ${ITK_LIBRARIES}
  )

#-----------------------------------------------------------------------------
# Build
#-----------------------------------------------------------------------------

# Each module in the extension is placed in it's own directory
add_subdirectory( BinShrink )
add_subdirectory( SimpleTest )
add_subdirectory( SpacingAwareCurvatureDiffusion )

add_subdirectory( DoubleThresholdEffect )

#-----------------------------------------------------------------------------
# Testing
#-----------------------------------------------------------------------------
if(BUILD_TESTING)
  add_subdirectory(Testing)
endif()

#-----------------------------------------------------------------------------
# Generate extension description file '<EXTENSION_NAME>.s4ext'
#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  include(SlicerFunctionGenerateExtensionDescription)
  slicerFunctionGenerateExtensionDescription(
    EXTENSION_NAME ${EXTENSION_NAME}
#    EXTENSION_BUILD_SUBDIRECTORY ${EXTENSION_BUILD_SUBDIRECTORY}
    EXTENSION_CATEGORY ${EXTENSION_CATEGORY}
    EXTENSION_ICONURL ${EXTENSION_ICONURL}
    EXTENSION_STATUS ${EXTENSION_STATUS}
    EXTENSION_HOMEPAGE ${EXTENSION_HOMEPAGE}
    EXTENSION_CONTRIBUTORS ${EXTENSION_CONTRIBUTORS}
    EXTENSION_DESCRIPTION ${EXTENSION_DESCRIPTION}
    EXTENSION_SCREENSHOTURLS ${EXTENSION_SCREENSHOTURLS}
    EXTENSION_DEPENDS ${EXTENSION_DEPENDS}
    DESTINATION_DIR ${CMAKE_CURRENT_BINARY_DIR}
    SLICER_WC_REVISION ${Slicer_WC_REVISION}
    SLICER_WC_ROOT ${Slicer_WC_ROOT}
    )
endif()

#-----------------------------------------------------------------------------
# Packaging
#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  include(${Slicer_EXTENSION_CPACK})
endif()
