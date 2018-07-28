
add_library(delay SHARED plugin.c)

install (TARGETS delay DESTINATION share/chaudio/plugins)

