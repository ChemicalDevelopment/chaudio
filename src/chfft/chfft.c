/*

wrapper around kiss fft stuff

*/

#include "chaudio.h"

#include "kissfft/kiss_fft.h"
#include "kissfft/kiss_fftr.h"

#include <complex.h>


chfft_plan_t chfft_fft_plan(int N) {
    chfft_plan_t r;
    r.N = N;
    r.is_inverse = false;
    r._internal = (void *)malloc(sizeof(kiss_fftr_cfg));
    *(kiss_fftr_cfg *)r._internal = kiss_fftr_alloc(N, 0, 0, 0);
    return r;
}

chfft_plan_t chfft_ifft_plan(int N) {
    chfft_plan_t r;
    r.N = N;
    r.is_inverse = true;
    r._internal = (void *)malloc(sizeof(kiss_fftr_cfg));
    *(kiss_fftr_cfg *)r._internal = kiss_fftr_alloc(N, 1, 0, 0);
    return r;
}

void chfft_plan_free(chfft_plan_t plan) {
    if (plan.N > 0 && plan._internal != NULL) {
        kiss_fftr_free(plan._internal);
        plan._internal = NULL;
    }
}

void chfft_doplan(double * audio_data, complex double * freq_data, chfft_plan_t plan) {
    if (plan.is_inverse) {
        kiss_fftri(*(kiss_fftr_cfg *)plan._internal, (kiss_fft_cpx *)freq_data, audio_data);
    } else {
        kiss_fftr(*(kiss_fftr_cfg *)plan._internal, audio_data, (kiss_fft_cpx *)freq_data);
    }
}




