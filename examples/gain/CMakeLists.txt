
add_library(gain SHARED gain.c)

install (TARGETS gain DESTINATION share/chaudio/plugins)

