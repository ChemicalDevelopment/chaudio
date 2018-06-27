#FILE(GLOB examples "${CMAKE_CURRENT_SOURCE_DIR}/*.")

#install (FILES ${examples} DESTINATION share/ezc/examples PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_WRITE GROUP_EXECUTE WORLD_READ WORLD_WRITE WORLD_EXECUTE)



# writing 
add_executable(ch_write example_write.c)
add_executable(ch_plugin example_plugin.c)
add_executable(ch_signal example_signal.c)

target_link_libraries(ch_write chaudio ${CMAKE_DL_LIBS})
target_link_libraries(ch_plugin chaudio ${CMAKE_DL_LIBS})
target_link_libraries(ch_signal chaudio ${CMAKE_DL_LIBS})



