/*

wavout.c - output to wave file


*/

#define GENERATOR_NAME "chaudio.wavin"

#include "chaudiogenerator.h"


typedef struct WavInData {

    int32_t channels, sample_rate;

    int64_t cur_off;

    char * file_name;

    int64_t read_N;
    int32_t read_channels, read_sample_rate;
    double * read_data;

} WavInData;


void * f_init(int32_t channels, int32_t sample_rate) {
    WavInData * data = malloc(sizeof(WavInData));

    data->channels = channels;
    data->sample_rate = sample_rate;

    data->read_data = NULL;

    data->file_name = NULL;

    //chaudio_read_wav_samples("read.wav", &data->read_data, &data->read_N, &data->read_channels, &data->read_sample_rate);

    data->cur_off = 0;

    return (void *)data;
}

int32_t f_set_double(void * _data, char * key, double val) {
    return CHAUDIO_CONTINUE;
}

int32_t f_set_int(void * _data, char * key, int32_t val) {
    return CHAUDIO_CONTINUE;
}

int32_t f_set_string(void * _data, char * key, char * val) {
    WavInData * data = (WavInData *)_data;

    if (streq(key, "file")) {
        // take them from a .wav file
        strkeep(data->file_name, val);
        int32_t res = chaudio_read_wav_samples(data->file_name, &data->read_data, &data->read_N, &data->read_channels, &data->read_sample_rate);
        if (res != 0) {
            printf("error reading file '%s'\n", val);
        }
        // reset to beginning of file
        data->cur_off = 0;
    }

    return CHAUDIO_CONTINUE;
}


int32_t f_set_audio(void * _data, char * key, audio_t val) {
    return CHAUDIO_CONTINUE;
}


int32_t f_generate(void * _data, double * out, int32_t N) {
    WavInData * data = (WavInData *)_data;

    int i, j;
    for (i = 0; i < N; ++i) {
        for (j = 0; j < data->channels; ++j) {
            if (data->read_data == NULL || i + data->cur_off >= data->read_N) {
                // just zero them out
                out[data->channels * i + j] = 0.0;
            } else if (j > data->read_channels) {
                out[data->channels * i + j] = data->read_data[data->read_channels * (i + data->cur_off) + 0];
            } else {
                out[data->channels * i + j] = data->read_data[data->read_channels * (i + data->cur_off) + j];
            }
        }
    }

    data->cur_off += N;

    if (data->cur_off > data->read_N) {
        // causes pipeline to finish
        return CHAUDIO_FINISHED;
    } else {
        return CHAUDIO_CONTINUE;
    }

}



// make sure to write wave file
int32_t f_free(void * _data) {
    WavInData * data = (WavInData *)_data;

    if (data->read_data != NULL) free(data->read_data);

    if (_data != NULL) free(_data);
    return CHAUDIO_CONTINUE;
}


chaudio_generator_t register_generator() {
    return chaudio_generator_create(GENERATOR_NAME, f_init, f_generate, f_free, chaudio_paraminterface_create(f_set_double, f_set_int, f_set_string, f_set_audio));
}


