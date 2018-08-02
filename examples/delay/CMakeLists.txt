
add_library(delay SHARED delay.c)

install (TARGETS delay DESTINATION share/chaudio/plugins)

