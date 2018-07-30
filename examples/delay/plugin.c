/*

Simple delay line plugin with feedback to illustrate how to use buffers

*/



#define PLUGIN_NAME "chaudio.delay"

#include "chaudioplugin.h"

// seconds
#define MAX_DELAY_TIME 10


typedef struct _DelayData {
    int32_t channels, sample_rate;

    // for storing where we are in `prev_data`
    int64_t cur_buf_idx;

    int64_t samples_stored;

    // channels * sample_rate * sizeof(double) * 10
    // for maximum of 10 seconds delay
    double * prev_data;

} DelayData;


void * f_init(int32_t channels, int32_t sample_rate, chdict_t * dict) {

    DelayData * data = malloc(sizeof(DelayData));

    data->channels = channels;
    data->sample_rate = sample_rate;

    data->samples_stored = data->sample_rate * MAX_DELAY_TIME;

    data->prev_data = malloc(sizeof(double) * data->samples_stored * data->channels);

    int i;
    for (i = 0; i < data->samples_stored * data->channels; ++i) {
        data->prev_data[i] = 0.0;
    }

    data->cur_buf_idx = 0;

    return (void *)data;
}

int32_t f_process(void * _data, double * in, double * out, int32_t N, chdict_t * dict) {
    DelayData * data = (DelayData *)_data;

    double delay_time = chdict_get_double(dict, "delay");    
    if (delay_time > (double)MAX_DELAY_TIME) delay_time = (double)MAX_DELAY_TIME;
    double feedback = chdict_get_double(dict, "feedback");


    int64_t delay_samples = (int64_t)(delay_time * data->sample_rate);
    int i, j;
    for (i = 0; i < N; ++i) {
        int64_t to_idx = ((data->cur_buf_idx + i) % data->samples_stored + data->samples_stored) % data->samples_stored;
        int64_t from_idx = ((data->cur_buf_idx + i - delay_samples) % data->samples_stored + data->samples_stored) % data->samples_stored;

        for (j = 0; j < data->channels; ++j) {
            data->prev_data[to_idx] = in[data->channels * i + j] + feedback * data->prev_data[from_idx];
            out[data->channels * i + j] = data->prev_data[from_idx];
        }
    }

    data->cur_buf_idx = (data->cur_buf_idx + N) % data->samples_stored;

    return 0;
}

int32_t f_free(void * _data) {
    if (_data != NULL) free(_data);
    return 0;
}

chaudio_plugin_t register_plugin() {
    return chaudio_plugin_create(PLUGIN_NAME, f_init, f_process, f_free);
}

