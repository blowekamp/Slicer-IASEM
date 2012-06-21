
#-----------------------------------------------------------------------------
set(MODULE_NAME EdgeLockerEffect)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  EdgeLockerEffect.py
  )

set(MODULE_PYTHON_RESOURCES
  EdgeLockerEffect.png
  )

#-----------------------------------------------------------------------------
ctkMacroCompilePythonScript(
  TARGET_NAME EdgeLockerEffect
  SCRIPTS "${MODULE_PYTHON_SCRIPTS}"
  RESOURCES "${MODULE_PYTHON_RESOURCES}"
  DESTINATION_DIR ${CMAKE_BINARY_DIR}/${Slicer_QTSCRIPTEDMODULES_LIB_DIR}
  INSTALL_DIR ${Slicer_INSTALL_ROOT}
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)
  add_subdirectory(Testing)
endif()
