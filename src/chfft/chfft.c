/*

wrapper around kiss fft stuff

*/

#include "chaudio.h"

#include "kissfft/kiss_fft.h"
#include "kissfft/kiss_fftr.h"

#include <complex.h>

chfft_t chfft_alloc(int Nsamples, int Nchannels, int sample_rate) {
    // make sure it's even
    if (Nsamples % 2 != 0) Nsamples++;
    chfft_t r;
    r.N_bins = Nsamples/2 + 1;
    r.N_channels = Nchannels;
    r.sample_rate = sample_rate;

    r.bins = malloc(sizeof(complex double) * Nchannels * r.N_bins);
    int i;
    for (i = 0; i < Nchannels * r.N_bins; ++i) {
        r.bins[i] = 0.0 + 0.0 * I;
    }
    return r;
}

void chfft_realloc(chfft_t * r, int Nsamples, int Nchannels) {
    if (Nsamples % 2 != 0) Nsamples++;
    r->N_bins = Nsamples/2 + 1;
    r->N_channels = Nchannels;
    r->bins = realloc(r->bins, sizeof(complex double) * r->N_bins * Nchannels);
}

void chfft_free(chfft_t * cf) {
    if (cf->bins != NULL) {
        free(cf->bins);
    } 
    cf->bins = NULL;
    cf->N_bins = 0;
    cf->sample_rate = 0;
    cf->N_channels = 0;
}

chfft_t chfft_fft(audio_t audio, chfft_t * res) {
    if (res == NULL) {
        chfft_t r = chfft_alloc(audio.length, audio.channels, audio.sample_rate);
        return chfft_fft(audio, &r);
    } else {
        chfft_realloc(res, audio.length, audio.channels);
        res->sample_rate = audio.sample_rate;
        kiss_fftr_cfg cfg = kiss_fftr_alloc(audio.length, 0, 0, 0);
        double * tmp = malloc(sizeof(double) * audio.length);
        int i, j;
        for (i = 0; i < audio.channels; ++i) {
            for (j = 0; j < audio.length; ++j) tmp[j] = audio.data[audio.channels * j + i];
            kiss_fftr(cfg, tmp, res->bins + (i * res->N_bins));
        }
        free(tmp);
        free(cfg);
        return *res;
    }
}

audio_t chfft_ifft(chfft_t freqs, audio_t * res) {
    if (res == NULL) {
        int Ns = 2 * (freqs.N_bins - 1);
        audio_t r = chaudio_audio_create(Ns, freqs.N_channels, freqs.sample_rate);
        return chfft_ifft(freqs, &r);
    } else {
        int Ns = 2 * (freqs.N_bins - 1);
        chaudio_audio_realloc(res, Ns, freqs.N_channels, freqs.sample_rate);
        kiss_fftr_cfg cfg = kiss_fftr_alloc(Ns, 1 /* is inverse fft */, 0, 0);
        double * tmp = malloc(sizeof(double) * Ns);
        int i, j;
        for (i = 0; i < freqs.N_channels; ++i) {
            kiss_fftri(cfg, freqs.bins + (i * freqs.N_bins), tmp);
            for (j = 0; j < Ns; ++j) res->data[res->channels * j + i] = tmp[j];
        }
        free(tmp);
        free(cfg);
        return *res;
    }
}

/*
chfft_plan_t chfft_ifft_plan(int N) {
    chfft_plan_t r;
    r.N = N;
    r.is_inverse = true;
    r._internal = (void *)malloc(sizeof(kiss_fftr_cfg));
    *(kiss_fftr_cfg *)r._internal = kiss_fftr_alloc(N, 1, 0, 0);
    return r;
}
*/




