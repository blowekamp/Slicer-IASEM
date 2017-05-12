
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
  --compare ${BASELINE}/${testname}.nrrd
            ${TEMP}/${testname}.nrrd
  ModuleEntryPoint
  --imageROI -6580,2817,421,47,49,62
  --input ${INPUT}/Gold3nmInLensA-roi100-164.mrc ${TEMP}/${testname}.nrrd )
set_property(TEST ${testname} PROPERTY LABELS ${CLP})

set(testname ${CLP}Test2)
add_test(NAME ${testname} COMMAND ${SEM_LAUNCH_COMMAND} $<TARGET_FILE:${CLP}Test>
  --compare ${BASELINE}/${testname}.nrrd
            ${TEMP}/${testname}.nrrd
  ModuleEntryPoint
  --bin "2"
  --input ${INPUT}/Gold3nmInLensA-roi100-164.mrc ${TEMP}/${testname}.nrrd )
set_property(TEST ${testname} PROPERTY LABELS ${CLP})

set(testname ${CLP}Test3)
add_test(NAME ${testname} COMMAND ${SEM_LAUNCH_COMMAND} $<TARGET_FILE:${CLP}Test>
  --compare ${BASELINE}/${testname}.nrrd
            ${TEMP}/${testname}.nrrd
  ModuleEntryPoint
  --bin "2,2"
  --input ${INPUT}/Gold3nmInLensA-roi100-164.mrc ${TEMP}/${testname}.nrrd )
set_property(TEST ${testname} PROPERTY LABELS ${CLP})

set(testname ${CLP}Test4)
add_test(NAME ${testname} COMMAND ${SEM_LAUNCH_COMMAND} $<TARGET_FILE:${CLP}Test>
  --compare ${BASELINE}/${testname}.nrrd
            ${TEMP}/${testname}.nrrd
  ModuleEntryPoint
  --bin "2,2,2"
  --input ${INPUT}/Gold3nmInLensA-roi100-164.mrc ${TEMP}/${testname}.nrrd )
set_property(TEST ${testname} PROPERTY LABELS ${CLP})

set(testname ${CLP}Test5)
add_test(NAME ${testname} COMMAND ${SEM_LAUNCH_COMMAND} $<TARGET_FILE:${CLP}Test>
  --compare ${BASELINE}/${testname}.nrrd
            ${TEMP}/${testname}.nrrd
  ModuleEntryPoint
  --bin "2,2,2"
  --disableZBin
  --input ${INPUT}/Gold3nmInLensA-roi100-164.mrc ${TEMP}/${testname}.nrrd )
set_property(TEST ${testname} PROPERTY LABELS ${CLP})

set(testname ${CLP}Test6)
add_test(NAME ${testname} COMMAND ${SEM_LAUNCH_COMMAND} $<TARGET_FILE:${CLP}Test>
  --compare ${BASELINE}/${testname}.nrrd
            ${TEMP}/${testname}.nrrd
  ModuleEntryPoint
  --bin "2,2"
  --imageROI -6580,2817,421,47,49,62
  --input ${INPUT}/Gold3nmInLensA-roi100-164.mrc ${TEMP}/${testname}.nrrd )
set_property(TEST ${testname} PROPERTY LABELS ${CLP})


set(testname ${CLP}Test7)
add_test(NAME ${testname} COMMAND ${SEM_LAUNCH_COMMAND} $<TARGET_FILE:${CLP}Test>
  --compare ${BASELINE}/${testname}.mrc
            ${TEMP}/${testname}.mrc
  ModuleEntryPoint
  --bin "2,2,10"
  --imageROI -6580,2817,421,47,49,62
  --input ${INPUT}/Gold3nmInLensA-roi100-164.mrc ${TEMP}/${testname}.mrc )
set_property(TEST ${testname} PROPERTY LABELS ${CLP})

