cmake_minimum_required(VERSION 2.8.8)

#-----------------------------------------------------------------------------
set(MODULE_NAME "SpacingAwareCurvatureDiffusion")

#-----------------------------------------------------------------------------
set(MODULE_HOMEPAGE "${_EXT_HOMEPAGE}")
set(MODULE_CATEGORY "${_EXT_CATEGORY}")
set(MODULE_CONTRIBUTORS "Bradley Lowekamp and Bill Lorensen (GE)")
set(MODULE_DESCRIPTION "Performs anisotropic diffusion on an image using a modified curvature diffusion equation (MCDE).\\n\\nMCDE does not exhibit the edge enhancing properties of classic anisotropic diffusion, which can under certain conditions undergo a 'negative' diffusion, which enhances the contrast of edges.  Equations of the form of MCDE always undergo positive diffusion, with the conductance term only varying the strength of that diffusion. \\n\\n Qualitatively, MCDE compares well with other non-linear diffusion techniques.  It is less sensitive to contrast than classic Perona-Malik style diffusion, and preserves finer detailed structures in images.  There is a potential speed trade-off for using this function in place of Gradient Anisotropic Diffusion.  Each iteration of the solution takes roughly twice as long.  Fewer iterations, however, may be required to reach an acceptable solution.\\n\\nThis a modifed derivation of the Curvature Anisotropic Diffusion module which scaled the time step by the minimum spacing, so that the this filter will automatically choose an optimal time step by default." )
set(MODULE_ACKNOWLEDGEMENTS "${_EXT_ACKNOWLEDGEMENTS}")
set(MODULE_LICENSE_SHORT_DESCRIPTION "${MODULE_LICENSE_SHORT_DESCRIPTION}")
set(MODULE_MAJOR_VERSION "${_EXT_MAJOR_VERSION}")
set(MODULE_MINOR_VERSION "${_EXT_MINOR_VERSION}")
set(MODULE_PATCH_VERSION "${_EXT_PATCH_VERSION}")

# Configure XML description
configure_file(
  ${MODULE_NAME}.xml.in
  ${CMAKE_CURRENT_BINARY_DIR}/${MODULE_NAME}.xml
  @ONLY
  )

#-----------------------------------------------------------------------------
set(MODULE_INCLUDE_DIRECTORIES
  )

set(MODULE_SRCS
  )

set(MODULE_TARGET_LIBRARIES
  ${ITK_LIBRARIES} ${SimpleITK_LIBRARIES}
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
