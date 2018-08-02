
add_subdirectory(gain)
add_subdirectory(delay)
add_subdirectory(flanger)
add_subdirectory(signal)
add_subdirectory(wavin)
add_subdirectory(wavout)

# writing 


add_executable(ch_write write.c)
add_executable(ch_realtime_pipeline realtime_pipeline.c)
add_executable(ch_pipeline pipeline.c)

add_executable(ch_build_info build_info.c)
add_executable(ch_extend extend.c)
add_executable(ch_profile profile.c)

add_executable(ch_plug chplug.c)


target_link_libraries(ch_build_info chaudio ${CMAKE_DL_LIBS})
target_link_libraries(ch_write chaudio ${CMAKE_DL_LIBS})
target_link_libraries(ch_extend chaudio ${CMAKE_DL_LIBS})
target_link_libraries(ch_profile chaudio ${CMAKE_DL_LIBS})
target_link_libraries(ch_realtime_pipeline chaudio ${CMAKE_DL_LIBS})
target_link_libraries(ch_pipeline chaudio ${CMAKE_DL_LIBS})

target_link_libraries(ch_plug chplug ${CMAKE_DL_LIBS})


# TODO: determine best place to store utilities
install (TARGETS ch_build_info ch_write ch_extend ch_profile ch_pipeline ch_realtime_pipeline DESTINATION bin)


