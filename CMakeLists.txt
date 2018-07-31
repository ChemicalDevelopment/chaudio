cmake_minimum_required (VERSION 2.6)

project (chaudio C)
set (CHAUDIO_VERSION_MAJOR 0)
set (CHAUDIO_VERSION_MINOR 1)

# options

option(BUILD_DOCS "Build documentation" OFF)
option(WITH_PORTAUDIO "Require portaudio for building chaudio" OFF)


set(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(CMAKE_C_FLAGS "-O2 -g -Wall -pedantic -std=c99 ${CMAKE_C_FLAGS}")

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -D__FILENAME__='\"$(subst ${CMAKE_SOURCE_DIR}/,,$(abspath $<))\"'")

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}")

configure_file (
  "${PROJECT_SOURCE_DIR}/chaudioconfig.h.in"
  "${PROJECT_BINARY_DIR}/chaudioconfig.h"
)

if (CMAKE_BUILD_TYPE MATCHES RELEASE)
    message("release mode")
    add_definitions(-DCHAUDIO_RELEASE)
else()
    message("dev mode")
    add_definitions(-DCHAUDIO_DEV)
endif()

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${chaudio_SOURCE_DIR}/cmake")

find_package(SDL2 REQUIRED)
find_package(PortAudio REQUIRED)


if (SDL2_FOUND)
    message(STATUS "Building with SDL2")
    add_definitions(-DHAVE_SDL2)
endif()

if (PORTAUDIO_FOUND)
    message(STATUS "Building with PortAudio")
    add_definitions(-DHAVE_PORTAUDIO)
elseif (WITH_PORTAUDIO)
    message(FATAL_ERROR "Could not find port audio")
endif()

include_directories("${PROJECT_BINARY_DIR}")
include_directories("${CMAKE_SOURCE_DIR}/src")

add_subdirectory (src)
if (BUILD_DOCS)
    add_subdirectory (docs) 
endif()
add_subdirectory (examples) 


install (FILES "${PROJECT_BINARY_DIR}/chaudioconfig.h" DESTINATION include)

# install all data
install (DIRECTORY "${PROJECT_SOURCE_DIR}/data" DESTINATION share/chaudio)



