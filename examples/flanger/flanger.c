/* examples/flanger/flanger.c -- https://en.wikipedia.org/wiki/Flanging

*/


#define PLUGIN_NAME "chaudio.flanger"

#include "chaudioplugin.h"


// data struct passed between functions
typedef struct _FlangerData {
    
    // basic stuff about the incoming stream
    int32_t channels, sample_rate;

    // plugin specific parameters
    double delay, depth, hz;

    int32_t prev_data_N;
    int32_t prev_data_off;
    double * prev_data;

    struct {
        double phase;
    } delay_osc;

} FlangerData;


void * f_init(int32_t channels, int32_t sample_rate) {
    printf("proc\n");

    FlangerData * data = malloc(sizeof(FlangerData));

    data->channels = channels;
    data->sample_rate = sample_rate;

    data->delay = 0.0;
    data->depth = 0.0;
    data->hz = 1.0;

    data->delay_osc.phase = 0.0;

    // store max one second of data
    data->prev_data_N = sample_rate;
    data->prev_data = malloc(sizeof(double) * channels * data->prev_data_N);
    data->prev_data_off = 0;

    return (void *)data;
}

int32_t f_set_double(void * _data, char * key, double val) {
    FlangerData * data = (FlangerData *)_data;
    if (streq(key, "delay")) {
        data->delay = val;
    } else if (streq(key, "depth")) {
        data->depth = val;
    } else if (streq(key, "hz")) {
        data->hz = val;
    }

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



int32_t f_process(void * _data, double * in, double * out, int32_t N) {

    FlangerData * data = (FlangerData *)_data;

    double delay = data->delay;
    double depth = data->depth;
    double hz = data->hz;

    double phase = data->delay_osc.phase;

    int i, j;
    for (i = 0; i < N; ++i) {
        double cdelay = delay + depth * (1.0 + sin(2.0 * M_PI * (phase + hz * i / data->sample_rate))) / 2.0;
        int64_t t_i = CIRCLEBUF_IDX(data->prev_data_off + i, data->prev_data_N);
        int64_t d_i = CIRCLEBUF_IDX(data->prev_data_off + i - (int64_t)floor(cdelay * data->sample_rate), data->prev_data_N);
        
        for (j = 0; j < data->channels; ++j) {
            // store previous data so it can be read back
            data->prev_data[data->channels * t_i + j] = in[data->channels * i + j];

            out[data->channels * i + j] = in[data->channels * i + j] + data->prev_data[data->channels * d_i + j];
        }
    }

    data->prev_data_off = (data->prev_data_off + N) % data->prev_data_N;

    data->delay_osc.phase = phase + (hz * N) / data->sample_rate;

    return 0;
}

int32_t f_free(void * _data) {
    if (_data != NULL) free(_data);
    return 0;
}

chaudio_plugin_t register_plugin() {
    return chaudio_plugin_create(PLUGIN_NAME, f_init, f_process, f_free, chaudio_paraminterface_create(f_set_double, f_set_int, f_set_string, f_set_audio));
}

