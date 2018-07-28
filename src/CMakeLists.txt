

add_library(chaudio STATIC dict.c util.c    chaudio.c plugin.c signal.c    chaudio.h)


target_link_libraries(chaudio m ${CMAKE_DL_LIBS})
target_compile_options(chaudio PUBLIC -std=c99 -fpermissive -w -Wall )


install (TARGETS chaudio DESTINATION lib)

install (FILES chaudio.h chaudiofunctions.h chaudioplugin.h DESTINATION include)

