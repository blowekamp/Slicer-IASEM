if( NOT Slicer_USE_SimpleITK )
  return()
endif()

# SimpleTest Module
#-----------------------------------------------------------------------------

set(MODULE_NAME "SpacingAwareCurvatureDiffusion")
set(MODULE_CONTRIBUTORS "Bill Lorensen (GE) and Bradley Lowekamp")
set(MODULE_DESCRIPTION "Performs anisotropic diffusion on an image using a modified curvature diffusion equation (MCDE).\\n\\nMCDE does not exhibit the edge enhancing properties of classic anisotropic diffusion, which can under certain conditions undergo a 'negative' diffusion, which enhances the contrast of edges.  Equations of the form of MCDE always undergo positive diffusion, with the conductance term only varying the strength of that diffusion. \\n\\n Qualitatively, MCDE compares well with other non-linear diffusion techniques.  It is less sensitive to contrast than classic Perona-Malik style diffusion, and preserves finer detailed structures in images.  There is a potential speed trade-off for using this function in place of Gradient Anisotropic Diffusion.  Each iteration of the solution takes roughly twice as long.  Fewer iterations, however, may be required to reach an acceptable solution.\\n\\nThis a modifed derivation of the Curvature Anisotropic Diffusion module which scaled the time step by the minimum spacing, so that the this filter will automatically choose an optimal time step by default." )

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