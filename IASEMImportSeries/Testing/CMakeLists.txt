#-----------------------------------------------------------------------------

# to avoid conflict with VTK's ExternalData CMake module, temporarily
# update module path
set(_CMAKE_MODULE_PATH CMAKE_MODULE_PATH)
set(CMAKE_MODULE_PATH "")
include(ExternalData)
set(CMAKE_MODULE_PATH _CMAKE_MODULE_PATH)

if(NOT ExternalData_OBJECT_STORES)
  # Use ExternalData_OBJECT_STORES from environment as default.
  set(ExternalData_OBJECT_STORES_DEFAULT "")
  if(DEFINED "ENV{ExternalData_OBJECT_STORES}")
    file(TO_CMAKE_PATH "$ENV{ExternalData_OBJECT_STORES}" ExternalData_OBJECT_STORES_DEFAULT)
    else()
      set(ExternalData_OBJECT_STORES ${Slicer_ExternalData_OBJECT_STORES})
  endif()
endif()

set(ExternalData_URL_TEMPLATES "http://placid.nlm.nih.gov/api/rest?method=midas.bitstream.download&checksum=%(hash)")

#-----------------------------------------------------------------------------
set(BASELINE ${CMAKE_CURRENT_SOURCE_DIR}/../Data/Baseline)
set(INPUT ${CMAKE_CURRENT_SOURCE_DIR}/../Data/Input)
set(TEMP ${CMAKE_BINARY_DIR}/Testing/Temporary)

set(CLP ${MODULE_NAME})


#-----------------------------------------------------------------------------
add_executable(${CLP}Test ${CLP}Test.cxx)
target_link_libraries(${CLP}Test ${CLP}Lib)
set_target_properties(${CLP}Test PROPERTIES LABELS ${CLP})


set(testname ${CLP}Test1)
ExternalData_Add_Test(Data NAME ${testname} COMMAND ${SEM_LAUNCH_COMMAND} $<TARGET_FILE:${CLP}Test>
  --compare DATA{${BASELINE}/${testname}.mrc}
            ${TEMP}/${testname}.mrc
  ModuleEntryPoint
   --bin 1,1,2
   --disableZBin
   --inputDirectory DATA{${INPUT}/InLens/,REGEX:.*.tif}
   ${TEMP}/${testname}.mrc )
set_property(TEST ${testname} PROPERTY LABELS ${CLP})


set(testname ${CLP}Test2)
ExternalData_Add_Test(Data NAME ${testname} COMMAND ${SEM_LAUNCH_COMMAND} $<TARGET_FILE:${CLP}Test>
  --compare DATA{${BASELINE}/${testname}.mrc}
            ${TEMP}/${testname}.mrc
  ModuleEntryPoint
   --bin 1,1,2
   --inputDirectory DATA{${INPUT}/InLens/,REGEX:.*.tif}
   --imodxg "${INPUT}/InLens/Gold3nmEsBTr.xg"
   ${TEMP}/${testname}.mrc )
set_property(TEST ${testname} PROPERTY LABELS ${CLP})


set(testname ${CLP}Test3)
ExternalData_Add_Test(Data NAME ${testname} COMMAND ${SEM_LAUNCH_COMMAND} $<TARGET_FILE:${CLP}Test>
  --compare DATA{${BASELINE}/${testname}.mrc}
            ${TEMP}/${testname}.mrc
  ModuleEntryPoint
   --bin 4,4,2
   --disableZBin
   --inputDirectory DATA{${INPUT}/InLens/,REGEX:.*.tif}
   --imodxg "${INPUT}/InLens/Gold3nmEsBTr.xg"
   ${TEMP}/${testname}.mrc )
set_property(TEST ${testname} PROPERTY LABELS ${CLP})


set(testname ${CLP}Test4)
ExternalData_Add_Test(Data NAME ${testname} COMMAND ${SEM_LAUNCH_COMMAND} $<TARGET_FILE:${CLP}Test>
  --compare DATA{${BASELINE}/${CLP}Test2.mrc}
            ${TEMP}/${testname}.nrrd
  ModuleEntryPoint
   --bin 1,1,2
   --inputDirectory DATA{${INPUT}/InLens/,REGEX:.*.tif}
   --imodxg "${INPUT}/InLens/Gold3nmEsBTr.xg"
   ${TEMP}/${testname}.nrrd )
set_property(TEST ${testname} PROPERTY LABELS ${CLP})

ExternalData_Add_Target(Data)
