
add_library(gain SHARED plugin.c)

install (TARGETS gain DESTINATION share/chaudio/plugins)

