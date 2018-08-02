
add_library(signal SHARED signal.c)

install (TARGETS signal DESTINATION share/chaudio/generators)

