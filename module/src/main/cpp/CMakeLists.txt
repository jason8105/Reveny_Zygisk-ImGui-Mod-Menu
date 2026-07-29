cmake_minimum_required(VERSION 3.18.1)

if (NOT DEFINED MODULE_NAME)
    # Default to 'reveny' if MODULE_NAME isn't passed from Gradle
    set(MODULE_NAME "reveny")
endif ()

project(${MODULE_NAME})

message("Build type: ${CMAKE_BUILD_TYPE}")

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(LINKER_FLAGS "-ffixed-x18 -Wl,--hash-style=both")
set(C_FLAGS "-Werror=format -fdata-sections -ffunction-sections")
set(CXX_FLAGS "${CXX_FLAGS} -fexceptions -frtti")

if (NOT CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(C_FLAGS "${C_FLAGS} -O2 -fvisibility=hidden -fvisibility-inlines-hidden")
    set(LINKER_FLAGS "${LINKER_FLAGS} -Wl,-exclude-libs,ALL -Wl,--gc-sections -Wl,--strip-all")
else ()
    set(C_FLAGS "${C_FLAGS} -O0")
endif ()

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${C_FLAGS}")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${C_FLAGS} ${CXX_FLAGS}")

set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} ${LINKER_FLAGS}")
set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS} ${LINKER_FLAGS}")

# Include Directories matching your folder hierarchy
include_directories(Headers)
include_directories(Include)
include_directories(External/ImGui)
include_directories(External/ImGui/backends)
include_directories(External/KittyMemory)
include_directories(External/Dobby)

add_library(${MODULE_NAME}
        SHARED
        Main.cpp
        Drawing.cpp
        ModMenu.cpp
        Utility.cpp
        External/ImGui/imgui.cpp
        External/ImGui/imgui_draw.cpp
        External/ImGui/imgui_demo.cpp
        External/ImGui/imgui_widgets.cpp
        External/ImGui/imgui_tables.cpp
        External/ImGui/backends/imgui_impl_opengl3.cpp
        External/ImGui/backends/imgui_impl_android.cpp
        External/KittyMemory/KittyMemory.cpp
        External/KittyMemory/MemoryPatch.cpp
        External/KittyMemory/MemoryBackup.cpp
        External/KittyMemory/KittyUtils.cpp
)

set(DOBBY_LIB ${CMAKE_CURRENT_SOURCE_DIR}/External/Dobby/libs/${CMAKE_ANDROID_ARCH_ABI}/libdobby.a)

find_library(log-lib log)
find_library(egl EGL)
find_library(android android)
find_library(GLESV2_LIB GLESv2)
find_library(GLESV3_LIB GLESv3)

if (${ANDROID_PLATFORM_LEVEL} LESS 12)
    message(FATAL_ERROR "OpenGL 2 is not supported before API level 12 / (currently using ${ANDROID_PLATFORM_LEVEL}).")
    return()
elseif (${ANDROID_PLATFORM_LEVEL} LESS 18)
    add_definitions("-DDYNAMIC_ES3")
    set(OPENGL_LIB GLESv2)
else ()
    set(OPENGL_LIB GLESv3)
endif ()

target_link_libraries(
        ${MODULE_NAME}
        log
        ${DOBBY_LIB}
        ${OPENGL_LIB}
        ${GLESV2_LIB}
        ${android}
        ${egl}
)

if (NOT CMAKE_BUILD_TYPE STREQUAL "Debug")
    add_custom_command(TARGET ${MODULE_NAME} POST_BUILD
            COMMAND ${CMAKE_STRIP} --strip-all --remove-section=.comment "${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/lib${MODULE_NAME}.so")
endif ()
