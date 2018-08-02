
add_library(wavin SHARED wavin.c)

install (TARGETS wavin DESTINATION share/chaudio/generators)

