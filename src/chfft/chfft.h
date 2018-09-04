/*

chfft - simple fft implementations

*/


#ifndef __CHFFT_H__
#define __CHFFT_H__

#include "chaudio.h"
#include <complex.h>


// similar to other plans or configurations
typedef struct _chfft_plan_s {

    int N;
    bool is_inverse;

    void * _internal;

} chfft_plan_t;

typedef struct _chfft_result_s {

    int N;

    double * bins;

} chfft_result_t;


chfft_plan_t chfft_fft_plan(int N);

chfft_plan_t chfft_ifft_plan(int N);

void chfft_doplan(double * audio_data, complex double * freq_data, chfft_plan_t plan);

#endif

