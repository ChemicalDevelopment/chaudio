
add_library(wavout SHARED wavout.c)

install (TARGETS wavout DESTINATION share/chaudio/outputs)

