/* examples/gain/plugin.c -- example chaudio plugin to show how to process signals in real time


*/


#define PLUGIN_NAME "chaudio.gain"

#include "chaudioplugin.h"


// data struct passed between functions
typedef struct _GainData {
    
    // basic stuff about the incoming stream
    int32_t channels, sample_rate;

    // plugin specific parameters
    double gain;

} GainData;


void * f_init(int32_t channels, int32_t sample_rate) {

    GainData * data = malloc(sizeof(GainData));

    data->channels = channels;
    data->sample_rate = sample_rate;

    data->gain = 0.0;

    return (void *)data;
}

int32_t f_set_double(void * _data, char * key, double val) {
    GainData * data = (GainData *)_data;
    if (streq(key, "gain")) {
        data->gain = val;
        return 0;
    } else {
        return 1;
    }
}

int32_t f_process(void * _data, double * in, double * out, int32_t N) {

    GainData * data = (GainData *)_data;

    double gain_coef = GAIN_COEF(data->gain);

    int i, j;
    for (i = 0; i < N; ++i) {
        for (j = 0; j < data->channels; ++j) {
            out[data->channels * i + j] = in[data->channels * i + j] * gain_coef;
        }
    }

    return 0;
}

int32_t f_free(void * _data) {
    if (_data != NULL) free(_data);
    return 0;
}

chaudio_plugin_t register_plugin() {
    return chaudio_plugin_create(PLUGIN_NAME, f_init, f_process, f_set_double, f_free);
}

