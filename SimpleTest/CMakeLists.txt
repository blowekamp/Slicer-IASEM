cmake_minimum_required(VERSION 2.8.8)

#-----------------------------------------------------------------------------
set(MODULE_NAME SimpleTest )

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  find_package(Slicer REQUIRED)
  include(${Slicer_USE_FILE})
endif()

#-----------------------------------------------------------------------------
set(MODULE_HOMEPAGE "${EXTENSION_HOMEPAGE}")
set(MODULE_CATEGORY "${EXTENSION_CATEGORY}")
set(MODULE_CONTRIBUTORS "${EXTENSION_CONTRIBUTORS}")
set(MODULE_DESCRIPTION "${EXTENSION_DESCRIPTION}")
set(MODULE_ACKNOWLEDGEMENTS "${EXTENSION_ACKNOWLEDGEMENTS}")
set(MODULE_MAJOR_VERSION "${EXTENSION_MAJOR_VERSION}")
set(MODULE_MINOR_VERSION "${EXTENSION_MINOR_VERSION}")
set(MODULE_PATCH_VERSION "${EXTENSION_PATCH_VERSION}")

#-----------------------------------------------------------------------------
# Configure XML description
configure_file(
  ${MODULE_NAME}.xml.in
  ${CMAKE_CURRENT_BINARY_DIR}/${MODULE_NAME}.xml
  @ONLY
  )

#-----------------------------------------------------------------------------
set(MODULE_TARGET_LIBRARIES
  ${ITK_LIBRARIES} ${SimpleITK_LIBRARIES}
  )
  
#-----------------------------------------------------------------------------
slicerMacroBuildCLI(
  NAME ${MODULE_NAME}
  TARGET_LIBRARIES ${MODULE_TARGET_LIBRARIES}
  )

