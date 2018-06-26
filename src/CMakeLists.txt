

add_library(chaudio chaudio.h)

install (TARGETS chaudio DESTINATION lib)


#add_executable(ec ec.c ec.h)

#target_link_libraries(ec ezc ${CMAKE_DL_LIBS})


install (FILES chaudio.h DESTINATION include)

