


# optional portaudio plugins for input/output
add_library(chaudio_input_portaudio SHARED input.c)
add_library(chaudio_output_portaudio SHARED output.c)

target_link_libraries(chaudio_input_portaudio ${PORTAUDIO_LIBRARIES})
target_link_libraries(chaudio_output_portaudio ${PORTAUDIO_LIBRARIES})

install (TARGETS chaudio_output_portaudio DESTINATION share/chaudio/plugins)
install (TARGETS chaudio_input_portaudio DESTINATION share/chaudio/plugins)


