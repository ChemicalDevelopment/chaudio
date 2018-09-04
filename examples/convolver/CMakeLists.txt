
add_library(convolver SHARED convolver.c)

install (TARGETS convolver DESTINATION share/chaudio/plugins)

