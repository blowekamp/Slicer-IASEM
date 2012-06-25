
#-----------------------------------------------------------------------------
set(MODULE_NAME WatershedFromMarkerEffect)

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
