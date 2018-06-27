

add_library(chaudio chaudio.c ch_util.c chaudio.h ch_util.h)



target_link_libraries(chaudio m ${CMAKE_DL_LIBS})
target_compile_options( chaudio PUBLIC -std=c99 -fpermissive -w -Wall )


install (TARGETS chaudio DESTINATION lib)



#add_executable(ec ec.c ec.h)



install (FILES chaudio.h DESTINATION include)

