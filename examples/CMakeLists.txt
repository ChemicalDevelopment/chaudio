
add_subdirectory(gain)
add_subdirectory(delay)

# writing 
add_executable(ch_build_info build_info.c)
add_executable(ch_write write.c)
add_executable(ch_signal signal.c)
add_executable(ch_plugin plugin.c)
add_executable(ch_extend extend.c)
add_executable(ch_profile profile.c)

target_link_libraries(ch_build_info chaudio ${CMAKE_DL_LIBS})
target_link_libraries(ch_write chaudio ${CMAKE_DL_LIBS})
target_link_libraries(ch_signal chaudio ${CMAKE_DL_LIBS})
target_link_libraries(ch_plugin chaudio ${CMAKE_DL_LIBS})
target_link_libraries(ch_extend chaudio ${CMAKE_DL_LIBS})
target_link_libraries(ch_profile chaudio ${CMAKE_DL_LIBS})

# TODO: determine best place to store utilities
install (TARGETS ch_build_info ch_write ch_signal ch_plugin ch_extend ch_profile DESTINATION bin)


