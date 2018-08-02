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

    // parameters
    double dry, delay, feedback;

} DelayData;


void * f_init(int32_t channels, int32_t sample_rate) {

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

    // defaults
    data->dry = 1.0;
    data->delay = 0.0;
    data->feedback = 0.0;
    

    return (void *)data;
}

int32_t f_set_double(void * _data, char * key, double val) {
    DelayData * data = (DelayData *)_data;
    if (streq(key, "dry")) {
        data->dry = val;
    } else if (streq(key, "delay")) {
        data->delay = val;
    } else if (streq(key, "feedback")) {
        data->feedback = val;
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
    DelayData * data = (DelayData *)_data;


    double dry = data->dry;
    double delay_time = data->delay;
    if (delay_time > (double)MAX_DELAY_TIME) delay_time = (double)MAX_DELAY_TIME;
    double feedback = data->feedback;


    int64_t delay_samples = (int64_t)(delay_time * data->sample_rate);
    int i, j;
    for (i = 0; i < N; ++i) {
        // CIRCLEBUF_IDX allows us to seamlessly loop back on the data
        int64_t to_idx = CIRCLEBUF_IDX(data->cur_buf_idx + i, data->samples_stored);
        int64_t from_idx = CIRCLEBUF_IDX(data->cur_buf_idx + i - delay_samples, data->samples_stored);

        for (j = 0; j < data->channels; ++j) {
            // update the other data
            data->prev_data[to_idx] = in[data->channels * i + j] + feedback * data->prev_data[from_idx];
            // combine the current and the echos
            out[data->channels * i + j] = dry * in[data->channels * i + j] + data->prev_data[from_idx];
        }
    }

    data->cur_buf_idx = CIRCLEBUF_IDX(data->cur_buf_idx + N, data->samples_stored);

    return 0;
}

int32_t f_free(void * _data) {
    if (_data != NULL) free(_data);
    return 0;
}

chaudio_plugin_t register_plugin() {
    return chaudio_plugin_create(PLUGIN_NAME, f_init, f_process, f_free, chaudio_paraminterface_create(f_set_double, f_set_int, f_set_string, f_set_audio));
}


