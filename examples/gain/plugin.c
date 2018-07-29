
#define PLUGIN_NAME "chaudio.gain"

#include "chaudioplugin.h"


typedef struct _GainData {
    int32_t channels, sample_rate;
} GainData;


void * f_init(int32_t channels, int32_t sample_rate, chdict_t * dict) {

    GainData * data = malloc(sizeof(GainData));

    data->channels = channels;
    data->sample_rate = sample_rate;

    return (void *)data;
}

int32_t f_process(void * _data, double * in, double * out, int32_t N, chdict_t * dict) {

    GainData * data = (GainData *)_data;

    double gain_coef = pow(10.0, chdict_get_double(dict, "gain") / 20.0);

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
    return chaudio_plugin_create(PLUGIN_NAME, f_init, f_process, f_free);
}

