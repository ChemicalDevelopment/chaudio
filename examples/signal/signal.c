/*

signal.c - generator for simple oscillator


*/

#define GENERATOR_NAME "chaudio.signal"

#include "chaudiogenerator.h"


typedef struct SignalData {

    int32_t channels, sample_rate;

    int32_t waveform;

    double phase;
    double hz;

} SignalData;

void * f_init(int32_t channels, int32_t sample_rate) {
    SignalData * data = malloc(sizeof(SignalData));

    data->channels = channels;
    data->sample_rate = sample_rate;

    data->waveform = CHAUDIO_WAVEFORM_SIN;
    data->phase = 0.0;
    data->hz = 440.0;

    return (void *)data;
}

int32_t f_set_double(void * _data, char * key, double val) {
    return CHAUDIO_CONTINUE;
}

int32_t f_set_int(void * _data, char * key, int32_t val) {
    return CHAUDIO_CONTINUE;
}

int32_t f_set_string(void * _data, char * key, char * val) {
    return CHAUDIO_CONTINUE;
}

int32_t f_set_audio(void * _data, char * key, audio_t val) {
    return CHAUDIO_CONTINUE;
}

int32_t f_generate(void * _data, double * out, int32_t N) {
    SignalData * data = (SignalData *)_data;


    int32_t waveform = data->waveform;
    double phase = data->phase;
    double hz = data->hz;

    int i, j;
    for (i = 0; i < N; ++i) {
        double c_s = sin(2 * M_PI * (hz * i / data->sample_rate + phase));

        for (j = 0; j < data->channels; ++j) {
            out[data->channels * i + j] = c_s;
        }
    } 


    data->phase = phase + hz * N / data->sample_rate;
    return CHAUDIO_CONTINUE;
}

int32_t f_free(void * _data) {
    if (_data != NULL) free(_data);
    return CHAUDIO_CONTINUE;
}


chaudio_generator_t register_generator() {
    return chaudio_generator_create(GENERATOR_NAME, f_init, f_generate, f_free, chaudio_paraminterface_create(f_set_double, f_set_int, f_set_string, f_set_audio));
}


