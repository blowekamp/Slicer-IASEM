if( NOT Slicer_USE_SimpleITK )
  return()
endif()

set(MODULE_NAME DoubleThresholdEffect)


#-----------------------------------------------------------------------------
# Sources
#-----------------------------------------------------------------------------
set(KIT_PYTHON_SCRIPTS
  DoubleThresholdEffect.py
  )

set(KIT_PYTHON_RESOURCES
  DoubleThresholdEffect.png
  )

#-----------------------------------------------------------------------------
# Build
#-----------------------------------------------------------------------------
ctkMacroCompilePythonScript(
  TARGET_NAME DoubleThresholdEffect
  SCRIPTS "${KIT_PYTHON_SCRIPTS}"
  RESOURCES "${KIT_PYTHON_RESOURCES}"
  DESTINATION_DIR ${CMAKE_BINARY_DIR}/${Slicer_QTSCRIPTEDMODULES_LIB_DIR}
  INSTALL_DIR ${Slicer_INSTALL_ROOT}
  )

#-----------------------------------------------------------------------------
# Testing
#-----------------------------------------------------------------------------
if(BUILD_TESTING)
  add_subdirectory(Testing)
endif()
