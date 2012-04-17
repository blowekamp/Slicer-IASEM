if( NOT Slicer_USE_SimpleITK )
  return()
endif()

# SimpleTest Module
#-----------------------------------------------------------------------------

set(MODULE_NAME SimpleTest )

# Configure XML description
configure_file(
  ${MODULE_NAME}.xml.in
  ${CMAKE_CURRENT_BINARY_DIR}/${MODULE_NAME}.xml
  @ONLY
  )

slicerMacroBuildCLI(
  NAME ${MODULE_NAME}
  #LOGO_HEADER ${Slicer_SOURCE_DIR}/Resources/NAMICLogo.h
  TARGET_LIBRARIES ${cli_module_target_libraries} ${SimpleITK_LIBRARIES}
  INCLUDE_DIRECTORIES ${cli_module_include_directories}
  ADDITIONAL_SRCS ${cli_module_SRCS}
  #EXECUTABLE_ONLY
  )