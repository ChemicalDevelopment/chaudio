/* examples/convolver/convolver.c -- example chaudio plugin to show how to conolve a signal by an impulse


*/


#define PLUGIN_NAME "chaudio.convolver"

#include "chaudioplugin.h"

#define HISTORY_DURATION 10

// data struct passed between functions
typedef struct _ConvolverData {
    
    // basic stuff about the incoming stream
    int32_t channels, sample_rate;

    double * history;

    // plugin specific parameters
    int64_t impulse_N;
    int32_t impulse_C;
    double * impulse;
    
    double complex * impulse_FFT;

    double complex * audio_FFT;

    double * convolved_signal;

    chfft_plan_t impulse_plan;
    chfft_plan_t inverse_plan;

} ConvolverData;


void * f_init(int32_t channels, int32_t sample_rate) {

    ConvolverData * data = malloc(sizeof(ConvolverData));

    data->channels = channels;
    data->sample_rate = sample_rate;

    data->history = malloc(sizeof(double) * channels * sample_rate * HISTORY_DURATION);

    data->impulse = NULL;
    data->impulse_FFT = NULL;
    data->audio_FFT = NULL;
    data->convolved_signal = NULL;

    data->impulse_plan.N = -1;

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
        int32_t _;

        int32_t res = chaudio_read_wav_samples(val, &data->impulse, &data->impulse_N, &data->impulse_C, &_);
        printf("%d\n", data->impulse_N);

        if (data->impulse_N % 2 != 0) {
            data->impulse_N++;
            data->impulse = realloc(data->impulse, sizeof(double) * data->impulse_N * data->impulse_C);
            int i;
            for (i = 0; i < data->impulse_C; ++i) {
                data->impulse[data->impulse_N * data->impulse_C - i - 1] = 0.0;
            }
        } 

        if (res != 0) {
            printf("error reading file '%s'\n", val);
        }

        data->impulse_FFT = realloc(data->impulse_FFT, sizeof(double complex) * (data->impulse_N / 2 + 1));
        data->audio_FFT = realloc(data->audio_FFT, sizeof(double complex) * (data->impulse_N / 2 + 1));
        data->convolved_signal = realloc(data->convolved_signal, sizeof(double) * data->impulse_N);
        
        chfft_plan_free(data->impulse_plan);
        chfft_plan_free(data->inverse_plan);

        data->impulse_plan = chfft_fft_plan(data->impulse_N);

        chfft_doplan(data->impulse, data->impulse_FFT, data->impulse_plan);


        data->inverse_plan = chfft_ifft_plan(data->impulse_N);
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

    for (i = 0; i < data->channels * (data->sample_rate * HISTORY_DURATION - N); ++i) {
        data->history[i] = data->history[i + data->channels * N];
    }

    for (i = data->channels * (data->sample_rate * HISTORY_DURATION - N); i < data->channels * data->sample_rate * HISTORY_DURATION; ++i) {
        data->history[i] = in[i - data->channels * (data->sample_rate * HISTORY_DURATION - N)];
    }

    chfft_doplan(data->history + ((HISTORY_DURATION * data->sample_rate - data->impulse_N) * data->channels), data->audio_FFT, data->impulse_plan);

    for (i = 0; i < data->impulse_N / 2 + 1; ++i) {
        data->audio_FFT[i] = data->audio_FFT[i] * data->impulse_FFT[i];
    }


    chfft_doplan(data->convolved_signal, data->audio_FFT, data->inverse_plan);


    for (i = 0; i < N; ++i) {
        out[i] = data->convolved_signal[i + data->impulse_N - N] / data->impulse_N;
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

