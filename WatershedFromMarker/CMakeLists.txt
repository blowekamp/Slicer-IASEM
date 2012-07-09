cmake_minimum_required(VERSION 2.8.8)

#-----------------------------------------------------------------------------
set(MODULE_NAME WatershedFromMarkerEffect)

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  find_package(Slicer REQUIRED)
  include(${Slicer_USE_FILE})
endif()


#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  WatershedFromMarkerEffect.py
  )

set(MODULE_PYTHON_RESOURCES
  WatershedFromMarkerEffect.png
  )

#-----------------------------------------------------------------------------
ctkMacroCompilePythonScript(
  TARGET_NAME WatershedFromMarkerEffect
  SCRIPTS "${MODULE_PYTHON_SCRIPTS}"
  RESOURCES "${MODULE_PYTHON_RESOURCES}"
  DESTINATION_DIR ${CMAKE_BINARY_DIR}/${Slicer_QTSCRIPTEDMODULES_LIB_DIR}
  INSTALL_DIR ${Slicer_INSTALL_ROOT}
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)
  add_subdirectory(Testing)
endif()
