
#-----------------------------------------------------------------------------
set(BASELINE ${CMAKE_CURRENT_SOURCE_DIR}/../Data/Baseline)
set(INPUT ${CMAKE_CURRENT_SOURCE_DIR}/../Data/Input)
set(TEMP ${CMAKE_BINARY_DIR}/Testing/Temporary)

set(CLP ${MODULE_NAME})


#-----------------------------------------------------------------------------
add_executable(${CLP}Test ${CLP}Test.cxx)
target_link_libraries(${CLP}Test ${CLP}Lib ${SlicerExecutionModel_EXTRA_EXECUTABLE_TARGET_LIBRARIES})
set_target_properties(${CLP}Test PROPERTIES LABELS ${CLP})


set(testname ${CLP}Test1)
add_test(NAME ${testname} COMMAND ${SEM_LAUNCH_COMMAND} $<TARGET_FILE:${CLP}Test>
  --compare ${BASELINE}/${testname}.mrc
            ${TEMP}/${testname}.mrc
  ModuleEntryPoint
   --bin 1,1,2
   --disableZBin
   --inputDirectory ${INPUT}/InLens/
   ${TEMP}/${testname}.mrc )
set_property(TEST ${testname} PROPERTY LABELS ${CLP})


set(testname ${CLP}Test2)
add_test(NAME ${testname} COMMAND ${SEM_LAUNCH_COMMAND} $<TARGET_FILE:${CLP}Test>
  --compare ${BASELINE}/${testname}.mrc
            ${TEMP}/${testname}.mrc
  ModuleEntryPoint
   --bin 1,1,2
   --inputDirectory ${INPUT}/InLens/
   --imodxg "${INPUT}/InLens/Gold3nmEsBTr.xg"
   ${TEMP}/${testname}.mrc )
set_property(TEST ${testname} PROPERTY LABELS ${CLP})


set(testname ${CLP}Test3)
add_test(NAME ${testname} COMMAND ${SEM_LAUNCH_COMMAND} $<TARGET_FILE:${CLP}Test>
  --compare ${BASELINE}/${testname}.mrc
            ${TEMP}/${testname}.mrc
  ModuleEntryPoint
   --bin 4,4,2
   --disableZBin
   --inputDirectory ${INPUT}/InLens/
   --imodxg "${INPUT}/InLens/Gold3nmEsBTr.xg"
   ${TEMP}/${testname}.mrc )
set_property(TEST ${testname} PROPERTY LABELS ${CLP})


set(testname ${CLP}Test4)
add_test(NAME ${testname} COMMAND ${SEM_LAUNCH_COMMAND} $<TARGET_FILE:${CLP}Test>
  --compare ${BASELINE}/${CLP}Test2.mrc
            ${TEMP}/${testname}.nrrd
  ModuleEntryPoint
   --bin 1,1,2
   --inputDirectory ${INPUT}/InLens/
   --imodxg "${INPUT}/InLens/Gold3nmEsBTr.xg"
   ${TEMP}/${testname}.nrrd )
set_property(TEST ${testname} PROPERTY LABELS ${CLP})

ExternalData_Add_Target(Data)
