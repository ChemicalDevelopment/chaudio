
add_subdirectory(chfft)

set (ext_files "")
set (ext_libs "")

if (PORTAUDIO_FOUND)
    add_subdirectory(optional/portaudio)
    set(ext_files ${ext_files} optional/portaudio/realtime_process.c)
    set(ext_libs ${ext_libs} ${PORTAUDIO_LIBRARIES})
endif()


set (chfft_files chfft/chfft.c chfft/kissfft/kiss_fft.c chfft/kissfft/kiss_fft.h chfft/kissfft/_kiss_fft_guts.h chfft/kissfft/kiss_fftr.h chfft/kissfft/kiss_fftr.c)

add_library(chaudio STATIC util.c    chaudio.c signal.c plugin.c generator.c paraminterface.c  output.c pipeline.c ${chfft_files}  ${ext_files}    chaudio.h)

target_link_libraries(chaudio m ${ext_libs} ${CMAKE_DL_LIBS})
target_compile_options(chaudio PUBLIC -std=c99 -fpermissive -w -Wall )


install (TARGETS chaudio DESTINATION lib)

install (FILES chaudio.h chaudiofunctions.h chaudioplugin.h DESTINATION include)

