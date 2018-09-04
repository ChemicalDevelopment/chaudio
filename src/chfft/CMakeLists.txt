
add_library(chfft STATIC chfft.c chfft.h kissfft/kiss_fft.c kissfft/kiss_fft.h kissfft/_kiss_fft_guts.h kissfft/kiss_fftr.h kissfft/kiss_fftr.c)

install (FILES chfft.h DESTINATION include)
