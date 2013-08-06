
#-----------------------------------------------------------------------------
set(BASELINE ${CMAKE_CURRENT_SOURCE_DIR}/../Data/Baseline)
set(INPUT ${CMAKE_CURRENT_SOURCE_DIR}/../Data/Input)
set(TEMP ${CMAKE_BINARY_DIR}/Testing/Temporary)

set(CLP ${MODULE_NAME})


#-----------------------------------------------------------------------------
add_executable(${CLP}Test ${CLP}Test.cxx)
target_link_libraries(${CLP}Test ${CLP}Lib)
set_target_properties(${CLP}Test PROPERTIES LABELS ${CLP})


set(testname ${CLP}Test-b444)
add_test(NAME ${testname} COMMAND ${SEM_LAUNCH_COMMAND} $<TARGET_FILE:${CLP}Test>
  --compare ${BASELINE}/${testname}.nrrd
            ${TEMP}/${testname}.nrrd
  ModuleEntryPoint
  ${INPUT}/${CLP}Test.nrrd  ${TEMP}/${testname}.nrrd
  --neighborhood 4,4,4 )
set_property(TEST ${testname} PROPERTY LABELS ${CLP})
