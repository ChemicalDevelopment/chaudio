/*

wrapper around kiss fft stuff

*/

#include "chfft.h"

#include "kissfft/kiss_fft.h"
#include "kissfft/kiss_fftr.h"

#include <complex.h>

chfft_plan_t chfft_fft_plan(int N) {
    chfft_plan_t r;
    r.N = N;
    r.is_inverse = false;
    r._internal = (void *)kiss_fftr_alloc(N, 0, 0, 0);
    return r;
}

chfft_plan_t chfft_ifft_plan(int N) {
    chfft_plan_t r;
    r.N = N;
    r.is_inverse = false;
    r._internal = (void *)kiss_fftr_alloc(N, 1, 0, 0);
    return r;
}

void chfft_doplan(double * audio_data, complex double * freq_data, chfft_plan_t plan) {
    kiss_fftr((kiss_fftr_cfg)plan._internal, audio_data, (kiss_fft_cpx *)freq_data);
}




