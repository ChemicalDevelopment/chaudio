/* examples/convolver/convolver.c -- example chaudio plugin to show how to conolve a signal by an impulse


*/


#define PLUGIN_NAME "chaudio.convolver"

#include "chaudioplugin.h"

#include "../../src/chfft/chfft.h"


#define HISTORY_DURATION 10

// data struct passed between functions
typedef struct _ConvolverData {
    
    // basic stuff about the incoming stream
    int32_t channels, sample_rate;

    double * history;

    // plugin specific parameters
    int64_t impulse_N;
    int impulse_C;
    double * impulse;

    chfft_plan_t plan;

} ConvolverData;


void * f_init(int32_t channels, int32_t sample_rate) {

    ConvolverData * data = malloc(sizeof(ConvolverData));

    data->channels = channels;
    data->sample_rate = sample_rate;

    data->history = malloc(sizeof(double) * channels * sample_rate * HISTORY_DURATION);

    data->impulse = NULL;

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
        int _;
        int32_t res = chaudio_read_wav_samples(val, &data->impulse, &data->impulse_N, &data->impulse_C, &_);
        if (res != 0) {
            printf("error reading file '%s'\n", val);
        }
        // reset to beginning of file
    }

    return CHAUDIO_CONTINUE;
}

int32_t f_set_audio(void * _data, char * key, audio_t val) {
    return CHAUDIO_CONTINUE;
}



int32_t f_process(void * _data, double * in, double * out, int32_t N) {

    ConvolverData * data = (ConvolverData *)_data;

    int i, j;

    for (i = data->channels * N; i < data->channels * data->sample_rate * HISTORY_DURATION; ++i) {
        data->history[i] = data->history[i - data->channels * N];
    }

    for (i = 0; i < N; ++i) {
        for (j = 0; j < data->channels; ++j) {
            data->history[data->channels * i + j] = in[data->channels * (N - i - 1) + j];
        }
    }


    for (i = 0; i < N; ++i) {
        for (j = 0; j < data->channels; ++j) {
            double csum = 0.0;
            int k;
            for (k = 0; k < data->impulse_N; ++k) {
                csum += data->impulse[k * data->impulse_C] * data->history[data->channels * (i + k) + j];
            }
            out[data->channels * i + j] = csum;
        }
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

