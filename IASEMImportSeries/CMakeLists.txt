cmake_minimum_required(VERSION 2.8.8)

#-----------------------------------------------------------------------------
set(MODULE_NAME IASEMImportSeries)

#-----------------------------------------------------------------------------
set(MODULE_HOMEPAGE "${_EXT_HOMEPAGE}")
set(MODULE_CATEGORY "${_EXT_CATEGORY}")
set(MODULE_CONTRIBUTORS "${_EXT_CONTRIBUTORS}")
set(MODULE_DESCRIPTION "Import a directory of tiffs from IASEM, applying a slice-to-slice transfrom, multi-resolution, and region of interest extraction.")
set(MODULE_ACKNOWLEDGEMENTS "${_EXT_ACKNOWLEDGEMENTS}")
set(MODULE_LICENSE_SHORT_DESCRIPTION "${MODULE_LICENSE_SHORT_DESCRIPTION}")
set(MODULE_MAJOR_VERSION "${_EXT_MAJOR_VERSION}")
set(MODULE_MINOR_VERSION "${_EXT_MINOR_VERSION}")
set(MODULE_PATCH_VERSION "${_EXT_PATCH_VERSION}")

#-----------------------------------------------------------------------------
# Configure XML description
configure_file(
  ${MODULE_NAME}.xml.in
  ${CMAKE_CURRENT_BINARY_DIR}/${MODULE_NAME}.xml
  @ONLY
  )

#-----------------------------------------------------------------------------
set(MODULE_INCLUDE_DIRECTORIES
  "${IASEMExtension_SOURCE_DIR}/External/itkStreamingSinc/include"
  )

set(MODULE_SRCS
  IASEMImport_Fibics.cxx
  IASEMImport_ReadXG.cxx
  IASEMImport_ComputeBoundingBox.cxx

  "${IASEMExtension_SOURCE_DIR}/External/itkStreamingSinc/src/itkStreamingProcessObject.cxx"
  )

set(MODULE_TARGET_LIBRARIES
  ${ITK_LIBRARIES}
  )

#-----------------------------------------------------------------------------
SEMMacroBuildCLI(
  NAME ${MODULE_NAME}
  TARGET_LIBRARIES ${MODULE_TARGET_LIBRARIES}
  INCLUDE_DIRECTORIES ${MODULE_INCLUDE_DIRECTORIES}
  ADDITIONAL_SRCS ${MODULE_SRCS}
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)
  add_subdirectory(Testing)
endif()
