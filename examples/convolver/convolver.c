/* examples/convolver/convolver.c -- example chaudio plugin to show how to conolve a signal by an impulse


*/


#define PLUGIN_NAME "chaudio.convolver"

#include "chaudioplugin.h"

#define HISTORY_DURATION 12

// data struct passed between functions
typedef struct _ConvolverData {
    
    // basic stuff about the incoming stream
    int32_t channels, sample_rate;

    double * history;

    audio_t impulse;

    chfft_t impulse_FFT;
    chfft_t current_FFT;

    audio_t convolved;
} ConvolverData;


void * f_init(int32_t channels, int32_t sample_rate) {

    ConvolverData * data = malloc(sizeof(ConvolverData));

    data->channels = channels;
    data->sample_rate = sample_rate;

    data->history = malloc(sizeof(double) * channels * sample_rate * HISTORY_DURATION);

    data->impulse = _cdl.chaudio_audio_create(1, data->channels, data->sample_rate);
    data->impulse_FFT = _cdl.chfft_alloc(2, data->channels, data->sample_rate);
    data->current_FFT = _cdl.chfft_alloc(2, data->channels, data->sample_rate);

    data->convolved = _cdl.chaudio_audio_create(1, data->channels, data->sample_rate);

    return (void *)data;
}

int32_t f_set_double(void * _data, char * key, double val) {
    return CHAUDIO_CONTINUE;
}

int32_t f_set_int(void * _data, char * key, int32_t val) {
    return CHAUDIO_CONTINUE;
}

int32_t f_set_string(void * _data, char * key, char * val) {
    ConvolverData * data = (ConvolverData *)_data;

    if (strcmp(key, "impulse") == 0) {

        _cdl.chaudio_audio_free(&data->impulse);

        data->impulse = _cdl.chaudio_audio_create_wav(val);

        if (data->impulse.length % 2 != 0) {
            _cdl.chaudio_pad(data->impulse, 1, &data->impulse);
        }

        _cdl.chfft_realloc(&data->impulse_FFT, data->impulse.length, data->channels);
        _cdl.chfft_realloc(&data->current_FFT, data->impulse.length, data->channels);
        _cdl.chfft_fft(data->impulse, &data->impulse_FFT);
    }

    return CHAUDIO_CONTINUE;
}

int32_t f_set_audio(void * _data, char * key, audio_t val) {
    return CHAUDIO_CONTINUE;
}



int32_t f_process(void * _data, double * in, double * out, int32_t N) {

    ConvolverData * data = (ConvolverData *)_data;

    int i, j;

    for (i = 0; i < data->channels * (data->sample_rate * HISTORY_DURATION - N); ++i) {
        data->history[i] = data->history[i + data->channels * N];
    }

    for (i = data->channels * (data->sample_rate * HISTORY_DURATION - N); i < data->channels * data->sample_rate * HISTORY_DURATION; ++i) {
        data->history[i] = in[i - data->channels * (data->sample_rate * HISTORY_DURATION - N)];
    }

    // use a proxy audio to act like an audio_t
    audio_t proxy;
    proxy.channels = data->channels;
    proxy.sample_rate = data->sample_rate;
    proxy.length = data->impulse.length;
    proxy.data = data->history + ((HISTORY_DURATION * data->sample_rate - data->impulse.length) * data->channels);
    
    _cdl.chfft_fft(proxy, &data->current_FFT);

    for (i = 0; i < data->current_FFT.N_bins * data->current_FFT.N_channels; ++i) {
        data->current_FFT.bins[i] *= data->impulse_FFT.bins[i];
    }

    _cdl.chfft_ifft(data->current_FFT, &data->convolved);

    for (i = 0; i < N; ++i) {
        out[i] = data->convolved.data[i + data->convolved.length - N] / data->convolved.length;
    }

    return 0;
}

int32_t f_free(void * _data) {
    if (_data != NULL) free(_data);
    return 0;
}

chaudio_plugin_t register_plugin() {
    return chaudio_plugin_create(PLUGIN_NAME, f_init, f_process, f_free, chaudio_paraminterface_create(f_set_double, f_set_int, f_set_string, f_set_audio));
}

