
add_library(flanger SHARED flanger.c)

install (TARGETS flanger DESTINATION share/chaudio/plugins)

