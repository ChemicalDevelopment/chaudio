/*

wavout.c - output to wave file


*/

#define OUTPUT_NAME "chaudio.wavout"

#include "chaudiooutput.h"


typedef struct WavOutData {

    int32_t channels, sample_rate;

    int32_t N;
    double * stream;

    char * file_name;

} WavOutData;


typedef struct wav_header_t {
    char riff[4];
    uint32_t file_size;

    // texts
    char wave[4];
    char format_chunk_marker[4];
     
    uint32_t format_length; // always 16

    // 1 is PCM (direct stuff), this should only ever be 1
    uint16_t format_type;

    // we use this for our metadata
    uint16_t channels;
    uint32_t sample_rate;

    // not very useful
    uint32_t byte_rate;
    uint16_t block_align;

    // precision and how to read
    uint16_t bits_per_sample;

    // text
    char data_chunk_header[4];
    uint32_t data_size;
} wav_header_t;



void * f_init(int32_t channels, int32_t sample_rate) {
    WavOutData * data = malloc(sizeof(WavOutData));

    data->channels = channels;
    data->sample_rate = sample_rate;

    data->stream = NULL;
    data->N = 0;
    
    data->file_name = NULL;

    return (void *)data;
}


int32_t f_set_double(void * _data, char * key, double val) {
    return CHAUDIO_CONTINUE;
}

int32_t f_set_int(void * _data, char * key, int32_t val) {
    return CHAUDIO_CONTINUE;
}

int32_t f_set_string(void * _data, char * key, char * val) {
    WavOutData * data = (WavOutData *)_data;

    if (streq(key, "file")) {
        strkeep(data->file_name, val);
    }
    return CHAUDIO_CONTINUE;
}

int32_t f_set_audio(void * _data, char * key, audio_t val) {
    return CHAUDIO_CONTINUE;
}



int32_t f_dump(void * _data, double * in, int32_t N) {
    WavOutData * data = (WavOutData *)_data;

    data->stream = realloc(data->stream, sizeof(double) * data->channels * (data->N + N));

    int i, j;
    for (i = 0; i < N; ++i) {
        for (j = 0; j < data->channels; ++j) {
            data->stream[data->channels * (data->N + i) + j] = in[data->channels * i + j];
        }
    } 

    data->N += N;

    return CHAUDIO_CONTINUE;
}



// make sure to write wave file
int32_t f_free(void * _data) {
    WavOutData * data = (WavOutData *)_data;

    wav_header_t wav_header;

    wav_header.riff[0] = 'R';
    wav_header.riff[1] = 'I';
    wav_header.riff[2] = 'F';
    wav_header.riff[3] = 'F';

    wav_header.wave[0] = 'W';
    wav_header.wave[1] = 'A';
    wav_header.wave[2] = 'V';
    wav_header.wave[3] = 'E';

    memcpy(wav_header.format_chunk_marker, "fmt ", 4);
    memcpy(wav_header.data_chunk_header, "data", 4);

    wav_header.format_length = 16;

    wav_header.format_type = 1; //1 is PCM, 3 is IEEE floating point

    wav_header.channels = (uint16_t)data->channels;
    
    wav_header.sample_rate = (uint32_t)data->sample_rate;

    // 16 bit integer
    int32_t bps = 16;

    wav_header.byte_rate = (uint32_t)(data->sample_rate * data->channels * bps / 8);
    wav_header.block_align = (uint16_t)(data->channels * bps / 8);
    wav_header.bits_per_sample = bps;

    int32_t data_size = data->N * data->channels * bps / 8;
    
    wav_header.data_size = data_size;
    wav_header.file_size = data_size + sizeof(wav_header);

    if (data->file_name != NULL) {

        FILE * fp = fopen(data->file_name, "w");

        if (fp == NULL) printf("Failed\n");

        printf("writing file '%s'...\n", data->file_name);

        //void * wav_file_result = (void *)malloc(data_size);
        fwrite(&wav_header, 1, sizeof(wav_header), fp);

        int i, j;
        for (i = 0; i < data->N; ++i) {
            for (j = 0; j < data->channels; ++j) {
                // cur sample
                double cs = data->stream[data->channels * i + j];
                if (cs < -1.0) cs = -1.0;
                else if (cs > 1.0) cs = 1.0;
                int16_t c_aliased = (int16_t)floor(cs * 32767.0);
                fwrite(&c_aliased, 1, sizeof(int16_t), fp);
            }
        }

        fclose(fp);

        printf("...done\n");
        free(data->file_name);
    } else {
        printf("warning: no file for wavout!\n");
    }

    if (_data != NULL) free(_data);
    return CHAUDIO_CONTINUE;
}


chaudio_output_t register_output() {
    return chaudio_output_create(OUTPUT_NAME, f_init, f_dump, f_free, chaudio_paraminterface_create(f_set_double, f_set_int, f_set_string, f_set_audio));
}


