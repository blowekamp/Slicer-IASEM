cmake_minimum_required(VERSION 2.8.8)

#-----------------------------------------------------------------------------
set(MODULE_NAME BinaryWatershedEffect)

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  find_package(Slicer REQUIRED)
  include(${Slicer_USE_FILE})
endif()

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  BinaryWatershedEffect.py
  )

set(MODULE_PYTHON_RESOURCES
  BinaryWatershedEffect.png
  )

#-----------------------------------------------------------------------------
ctkMacroCompilePythonScript(
  TARGET_NAME BinaryWatershedEffect
  SCRIPTS "${MODULE_PYTHON_SCRIPTS}"
  RESOURCES "${MODULE_PYTHON_RESOURCES}"
  DESTINATION_DIR ${CMAKE_BINARY_DIR}/${Slicer_QTSCRIPTEDMODULES_LIB_DIR}
  INSTALL_DIR ${Slicer_INSTALL_ROOT}
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)
#  add_subdirectory(Testing)
endif()
