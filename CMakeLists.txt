cmake_minimum_required(VERSION 3.24)
project(IRProof VERSION 1.0.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
find_package(LLVM REQUIRED CONFIG)
if(LLVM_VERSION_MAJOR LESS 23)
  message(FATAL_ERROR "IRProof requires LLVM 23 or newer")
endif()
message(STATUS "IRProof: LLVM ${LLVM_PACKAGE_VERSION} (${LLVM_DIR})")
list(APPEND CMAKE_MODULE_PATH "${LLVM_CMAKE_DIR}")
include(AddLLVM)
include(HandleLLVMOptions)
include_directories(SYSTEM ${LLVM_INCLUDE_DIRS})
separate_arguments(IRPROOF_LLVM_DEFINITIONS NATIVE_COMMAND "${LLVM_DEFINITIONS}")
add_definitions(${IRPROOF_LLVM_DEFINITIONS})

add_llvm_pass_plugin(IRProofPass
  src/Plugin.cpp
  src/StrengthReduction.cpp
  src/Audit.cpp
)
target_include_directories(IRProofPass PRIVATE include)
target_compile_options(IRProofPass PRIVATE -Wall -Wextra -Wpedantic)

add_executable(irproof-gen tools/irproof-gen.cpp)
llvm_map_components_to_libnames(IRPROOF_LLVM_LIBS Core Support Analysis)
target_link_libraries(irproof-gen PRIVATE ${IRPROOF_LLVM_LIBS})
target_compile_options(irproof-gen PRIVATE -Wall -Wextra -Wpedantic)

include(CTest)
if(BUILD_TESTING)
  find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
  add_test(NAME irproof.unit COMMAND ${Python3_EXECUTABLE} -m unittest discover -s tests/unit -v)
  set_tests_properties(irproof.unit PROPERTIES WORKING_DIRECTORY ${PROJECT_SOURCE_DIR})
  add_test(NAME irproof.integration COMMAND ${Python3_EXECUTABLE} scripts/check_plugin.py
    --opt ${LLVM_TOOLS_BINARY_DIR}/opt --lli ${LLVM_TOOLS_BINARY_DIR}/lli
    --plugin $<TARGET_FILE:IRProofPass> --generator $<TARGET_FILE:irproof-gen>)
  set_tests_properties(irproof.integration PROPERTIES WORKING_DIRECTORY ${PROJECT_SOURCE_DIR})
endif()
