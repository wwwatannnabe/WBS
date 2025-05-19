cmake_minimum_required(VERSION 3.5)
project(p4factory VERSION 9.7.0 LANGUAGES C CXX)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "RelWithDebInfo" CACHE STRING
  "Choose the type of build, options are: None Debug Release RelWithDebInfo MinSizeRel."
  FORCE)
endif()
if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
  set(CMAKE_INSTALL_PREFIX "${CMAKE_CURRENT_SOURCE_DIR}/install" CACHE PATH "..." FORCE)
endif()

set(BF_PKG_DIR "pkgsrc")

set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_C_STANDARD 99)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_INSTALL_PREFIX}/lib")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_INSTALL_PREFIX}/lib")
set(CMAKE_PREFIX_PATH "${CMAKE_INSTALL_PREFIX}")


# p4 specific options
option(TOFINO        "Architecture: Build P4 for tofino" ON)
option(TOFINO2       "Architecture: Build P4 for tofino2" OFF)
option(TOFINO2M      "Architecture: Build P4 for tofino2m" OFF)
option(TOFINO2H      "Architecture: Build P4 for tofino2h" OFF)

# thrift settings
option(THRIFT-DRIVER "Drivers: Build with support for Thrift in bf-drivers and bf-platforms" ON)
option(THRIFT-DIAGS  "BF-Diags: Build with support for Thrift in bf-diags" ON)
option(THRIFT-SWITCH "Switch: Build with support for Thrift in switch-p4-16" ON)

# driver options
option(GRPC          "Drivers: Build with support for GRPC/protobuf" ON)
option(BFRT          "Drivers: Build with BFRuntime support" ON)
option(BFRT-GENERIC-FLAGS "Drivers: Build BF-RT C API with generic flags support" ON)
option(PI            "Drivers: Build with tofino PI backend support" OFF)
option(P4RT          "Drivers: Build with P4Runtime server in bf_switchd support" OFF)

option(SWITCH        "Switch: Build switch-p4-16 package" OFF)
option(SAI           "Switch: Build switch-p4-16 SAI implementation" ON)
option(BF-DIAGS      "BF-Diags: Build bf-diags package" OFF)

# tools
option(COVERAGE      "Build with gcov support" OFF)
option(TCMALLOC      "Build with gperftools" ON)
option(PROFILER      "Build with CPU profiler" OFF)
option(ASAN          "Build with ASAN" OFF)
option(LTO           "Build with LinkTimeOptimization" OFF)
option(FORCE32       "Force a 32bit compile on 64bit" OFF)
option(BF-PYTHON     "Build and enable bf-python CLI" ON)

# global
option(ASIC          "Build for ASIC" OFF)
option(CPUVETH       "Use CPU eth port, applicable for model" ON)

# bf-platform specific
option(BSP           "BF-Platforms: Build with Intel reference platform code" OFF)
option(TCLONLY       "BF-Platforms: Build only tcl server in bf-platforms" OFF)
option(NEWPORT       "BF-Platforms: Build Newport Platform" OFF)
option(ACCTON-DIAGS  "BF-Platforms: Build Accton Diags" OFF)
option(NEWPORT-DIAGS "BF-Platforms: Build Newport Diags" OFF)

# uncommon
option(BFSYS-DEBUG-MODE "Build bf-syslibs in debug mode" OFF)

include(ConfigureChecks)

set(PYTHON_EXECUTABLE python3)

include_directories(${CMAKE_CURRENT_BINARY_DIR})

if (THRIFT-DRIVER OR THRIFT-SWITCH OR THRIFT-DIAGS)
  find_package(Thrift REQUIRED)
endif()

#ptf-utils and bf-pktpy
set(PTF_PKG_DIR "ptf-modules")
add_subdirectory(${BF_PKG_DIR}/${PTF_PKG_DIR}/ptf-utils)
execute_process(
  COMMAND ${PYTHON_EXECUTABLE} -c "if True:
    from distutils import sysconfig as sc
    print(sc.get_python_lib(prefix='', standard_lib=True, plat_specific=True))"
  OUTPUT_VARIABLE PYTHON_SITE
  OUTPUT_STRIP_TRAILING_WHITESPACE)
set(PYTHON_SITE "${PYTHON_SITE}/site-packages")
install(PROGRAMS ${CMAKE_CURRENT_SOURCE_DIR}/${BF_PKG_DIR}/${PTF_PKG_DIR}/bf-ptf/ptf DESTINATION bin RENAME bf-ptf)
install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/${BF_PKG_DIR}/${PTF_PKG_DIR}/bf-ptf/src/ DESTINATION ${PYTHON_SITE}/bf-ptf)
install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/${BF_PKG_DIR}/${PTF_PKG_DIR}/bf-pktpy/bf_pktpy DESTINATION ${PYTHON_SITE})

if(NOT EXTRA_CPPFLAGS)
  set(EXTRA_CPPFLAGS "" CACHE STRING "" FORCE)
else()
  message(STATUS "\nEXTRA_CPPFLAGS: ${EXTRA_CPPFLAGS}")
endif()

set(C_CXX_FLAGS "-Wall -Wextra -Werror -Wshadow -Wpedantic -Wno-missing-field-initializers -DBF_SYS_LOG_FORMAT_CHECK ${EXTRA_CPPFLAGS}")
set(CMAKE_C_FLAGS   "${CMAKE_C_FLAGS}   ${C_CXX_FLAGS}")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${C_CXX_FLAGS}")

# if lto is ready, build lto for all targets after this configruation
if(LTO)
  set(CMAKE_C_FLAGS   "${CMAKE_C_FLAGS}   -flto=thin -fno-fat-lto-objects")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -flto=thin -fno-fat-lto-objects")
endif()

if(COVERAGE)
  set(CMAKE_C_FLAGS   "${CMAKE_C_FLAGS}   --coverage")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --coverage")
endif()
if(FORCE32)
  set(CMAKE_C_FLAGS   "${CMAKE_C_FLAGS}   -m32")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -m32")
endif()
if(CMAKE_COMPILER_IS_GNUCC AND (CMAKE_CXX_COMPILER_VERSION VERSION_LESS 5.0.0))
  set(CMAKE_C_FLAGS   "${CMAKE_C_FLAGS}   -Wno-error")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-error")
endif()
if(ASAN)
  SET(TCMALLOC OFF CACHE BOOL "Use malloc from LIBC for ASAN" FORCE)
  set(CMAKE_C_FLAGS   "${CMAKE_C_FLAGS}   -fsanitize=address -fsanitize-recover=address -fsanitize=leak")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address -fsanitize-recover=address -fsanitize=leak")
  set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fsanitize=address -fsanitize-recover=address -fsanitize=leak")
  set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS} -fsanitize=address -fsanitize-recover=address -fsanitize=leak")
endif()
if(NEWPORT)
  SET(TOFINO OFF CACHE BOOL "Do not build Tofino platform for Newport" FORCE)
  if(NOT TOFINO2M AND NOT TOFINO2H)
    SET(TOFINO2 ON CACHE BOOL "Build for Tofino2 ASIC" FORCE)
  endif()
endif()
if(ASIC)
  SET(CPUVETH OFF CACHE BOOL "CPUVETH is disabled for ASIC" FORCE)
endif()
if (P4RT)
  set(PI ON CACHE BOOL "PI is enabled if P4RT is on" FORCE)
  set(GRPC ON CACHE BOOL "GRPC is enabled if P4RT is on" FORCE)
endif()

if (STATIC-LINK-LIB)
  add_definitions(-DSTATIC_LINK_LIB)
endif()

# p4flags will be appended to internal compiler options
if(NOT P4FLAGS)
  set(P4FLAGS "" CACHE STRING "" FORCE)
else()
  message(STATUS "\nP4FLAGS: ${P4FLAGS}")
endif()

# p4ppflags will be appended to internal compiler options
if(NOT P4PPFLAGS)
  set(P4PPFLAGS "" CACHE STRING "" FORCE)
else()
  message(STATUS "\nP4PPFLAGS: ${P4PPFLAGS}")
endif()

#sys
message(STATUS "\nBegin bf-syslibs setup")
include_directories(${BF_PKG_DIR}/bf-syslibs/include)
include_directories(${BF_PKG_DIR}/bf-syslibs/third-party)
add_subdirectory(${BF_PKG_DIR}/bf-syslibs)

#utils
message(STATUS "\nBegin bf-utils setup")
include_directories(${BF_PKG_DIR}/bf-utils/third-party/tommyds/include)
include_directories(${BF_PKG_DIR}/bf-utils/third-party/xxhash/include)
include_directories(${BF_PKG_DIR}/bf-utils/third-party/cjson/include)
include_directories(${BF_PKG_DIR}/bf-utils/third-party/judy-1.0.5/src)
include_directories(${BF_PKG_DIR}/bf-utils/third-party/bigcode/include)
include_directories(${BF_PKG_DIR}/bf-utils/third-party/klish)
include_directories(${BF_PKG_DIR}/bf-utils/third-party/libedit-3.1/src)
include_directories(${BF_PKG_DIR}/bf-utils/third-party/bf-python/Include)
include_directories(${CMAKE_CURRENT_BINARY_DIR}/${BF_PKG_DIR}/bf-utils/third-party/libpython3.4m/src/libpython3.4m-build/)
include_directories(${BF_PKG_DIR}/bf-utils/include)
add_subdirectory(${BF_PKG_DIR}/bf-utils)

#drivers
message(STATUS "\nBegin bf-drivers setup")
include_directories(${BF_PKG_DIR}/bf-drivers)
include_directories(${BF_PKG_DIR}/bf-drivers/include)
add_subdirectory(${BF_PKG_DIR}/bf-drivers)

#compiler/model
include(FindP4CModel)

if(ASIC AND BSP)
  #platform
  message(STATUS "\nBegin bf-platforms setup")
  include_directories(${BF_PKG_DIR}/bf-diags/api/include)
  add_subdirectory(${BF_PKG_DIR}/bf-platforms)
endif()

#diags
if(BF-DIAGS)
  message(STATUS "\nBegin bf-diags setup")
  add_subdirectory(${BF_PKG_DIR}/bf-diags)
endif()

#switch
if(SWITCH)
  message(STATUS "\nBegin switch-p4-16 setup")
  add_subdirectory(${BF_PKG_DIR}/switch-p4-16)
endif()

#p4-examples
message(STATUS "\nBegin p4-examples setup")
add_subdirectory(${BF_PKG_DIR}/p4-examples)

file(WRITE ${CMAKE_INSTALL_PREFIX}/share/VERSION ${PROJECT_VERSION})
