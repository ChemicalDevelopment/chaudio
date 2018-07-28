
#include "chaudio.h"

#include "util.h"

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>

#include "chaudioconfig.h"


// internal structure for wave header

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


// epoch
double chaudio_start_time = 0.0;

int32_t chaudio_init() {

    chaudio_start_time = chaudio_time();

    return 0;
}


#include <sys/time.h>

// get time since `chaudio_init` was called, OR since the epoch if you haven't called chaudio_init
double chaudio_time() {

    struct timeval cur;
    gettimeofday(&cur, NULL);

    double time_since_epoch = (double)cur.tv_sec + cur.tv_usec / 1000000.0;

    return time_since_epoch - chaudio_start_time;
}


// used so it doesn't need to be realloc'd or anything
char * _build_res = NULL;

char * chaudio_get_build_info() {

    if (_build_res == NULL) {
        _build_res = malloc(4096);

        sprintf(_build_res, "chaudio v%d.%d", CHAUDIO_VERSION_MAJOR, CHAUDIO_VERSION_MINOR);
        #if CHAUDIO_DEV
        sprintf(_build_res, "%s (development build)", _build_res);
        #elif CHAUDIO_RELEASE
        sprintf(_build_res, "%s (release)", _build_res);
        #else
        sprintf(_build_res, "%s (unknown build)", _build_res);
        #endif

        sprintf(_build_res, "%s on %s at %s", _build_res, __DATE__, __TIME__);

        #ifdef HAVE_SDL2
        sprintf(_build_res, "%s (built with SDL2)", _build_res);
        #endif

    }

    return _build_res;
}


// initialization stuff
audio_t chaudio_audio_create(int64_t length, int32_t channels, int32_t sample_rate) {
    audio_t audio;

    audio.length = length;
    audio.channels = channels;
    audio.sample_rate = sample_rate;

    // NULL so realloc works
    if (channels == 0 || length == 0) audio.data = NULL;
    else {
        audio.data = (double *)malloc(sizeof(double) * audio.channels * audio.length);
        if (audio.data == NULL) {
            printf("OUT OF MEMORY\n");
            exit(1);
        }
    }

    int i;
    for (i = 0; i < audio.channels * audio.length; ++i) {
        audio.data[i] = 0.0;
    }
    return audio;
}

audio_t chaudio_audio_create_nothing() {
    return chaudio_audio_create(0, 0, CHAUDIO_DEFAULT_SAMPLE_RATE);
}

audio_t chaudio_audio_create_audio(audio_t from) {
    audio_t audio;

    audio.channels = from.channels;
    audio.length = from.length;
    audio.sample_rate = from.sample_rate;

    audio.data = malloc(sizeof(double) * audio.channels * audio.length);
    
    int i;
    for (i = 0; i < audio.channels * audio.length; ++i) {
        audio.data[i] = from.data[i];
    }

    return audio;
}

audio_t chaudio_audio_create_wav_fp(FILE * fp) {
    // struct to store data 
    wav_header_t wave_header;

    // read packed data
    fread(&wave_header, sizeof(wave_header), 1, fp);

    audio_t audio;

    audio.sample_rate = wave_header.sample_rate;
    audio.channels = wave_header.channels;
    audio.length = 8 * wave_header.data_size / (wave_header.channels * wave_header.bits_per_sample);
    
    audio.data = (double *)malloc(sizeof(double) * audio.length * audio.channels); 
    if (audio.data == NULL) {
        printf("OUT OF MEMORY\n");
        exit(1);
    }

    void * wave_data = (void *)malloc(wave_header.data_size);

    fread(wave_data, wave_header.data_size, BUFSIZ, fp);

    int i, j;
    if (wave_header.format_type == 3) { // IEEE floating point
        if (wave_header.bits_per_sample == 8 * sizeof(float)) { // 'float' type
            float * wave_floats = (float *)wave_data;
            for (i = 0; i < audio.length; ++i) {
                for (j = 0; j < audio.channels; ++j) {
                    audio.data[audio.length * j + i] = wave_floats[audio.channels * i + j];
                }
            } 
        } else if (wave_header.bits_per_sample == 8 * sizeof(double)) { // 'double' type
            double * wave_doubles = (double *)wave_data;
            for (i = 0; i < audio.length; ++i) {
                for (j = 0; j < audio.channels; ++j) {
                    audio.data[audio.length * j + i] = wave_doubles[audio.channels * i + j];
                }
            } 
        } else {
            printf("unknown floating point type\n");
            return AUDIO_NULL;
        }
    
    } if (wave_header.format_type == 1 || true) { //standard PCM packed fixed point, or assume all others are this
        if (wave_header.bits_per_sample == 8 * sizeof(int8_t)) {
            int8_t * wave_int8s = (int8_t *)wave_data;
            double tmp;
            for (i = 0; i < audio.length; ++i) {
                for (j = 0; j < audio.channels; ++j) {
                    tmp = (double)wave_int8s[audio.channels * i + j] / 128.0;
                    audio.data[audio.length * j + i] = tmp;
                }
            } 
        } else if (wave_header.bits_per_sample == 8 * sizeof(int16_t)) {
            int16_t * wave_int16s = (int16_t *)wave_data;
            double tmp;
            for (i = 0; i < audio.length; ++i) {
                for (j = 0; j < audio.channels; ++j) {
                    tmp = (double)wave_int16s[audio.channels * i + j] / 32768.0;
                    audio.data[audio.length * j + i] = tmp;
                }
            } 
        } else if (wave_header.bits_per_sample == 8 * 3) { // special 24 bit format
            
            int8_t * wave_int8packed = (int8_t *)wave_data;
            int64_t constructed = 0;
            double tmp;
            for (i = 0; i < audio.length; ++i) {
                for (j = 0; j < audio.channels; ++j) {
                    int pack_idx = audio.channels * i + j;
                    constructed = wave_int8packed[3 * pack_idx + 0] + (wave_int8packed[3 * pack_idx + 1] << 8) + (wave_int8packed[3 * pack_idx + 1] << 16);
                    tmp = (double)constructed / 8388608.0;
                    audio.data[audio.length * j + i] = tmp;
                }
            } 
        } else if (wave_header.bits_per_sample == 8 * sizeof(int32_t)) {
            int32_t * wave_int32s = (int32_t *)wave_data;
            double tmp;
            for (i = 0; i < audio.length; ++i) {
                for (j = 0; j < audio.channels; ++j) {
                    tmp = (double)wave_int32s[audio.channels * i + j] / 2147483648.0;
                    audio.data[audio.length * j + i] = tmp;
                }
            } 
        } 
    }
    
    free(wave_data);

    return audio;
}


// need to read in file
audio_t chaudio_audio_create_wav(char * file_path) {
    // open the file for reading
    FILE * fp = fopen(file_path, "r");

    if (fp == NULL) {
        printf("opening file failed for '%s'\n", file_path);
        return AUDIO_NULL;
    }

    audio_t audio = chaudio_audio_create_wav_fp(fp);

    fclose(fp);

    return audio;
}


int32_t chaudio_audio_realloc(audio_t * audio, int64_t new_length, int32_t new_channels, int32_t new_sample_rate) {
    //printf("entering \n");
    if (audio == NULL) {
        return -1;
    }

    int64_t old_length = audio->length;
    int32_t old_channels = audio->channels;

    //printf(" setting members\n");
    if (new_length != 0) audio->length = new_length;
    if (new_channels != 0) audio->channels = new_channels;
    if (new_sample_rate != 0) audio->sample_rate = new_sample_rate;

    //printf(" calling func\n");
    audio->data = (double *)realloc((void *)audio->data, sizeof(double) * audio->channels * audio->length);

    int i, j;
    for (i = 0; i < audio->channels; ++i) {
        for (j = (i >= old_channels ? 0 : old_length); j < audio->length; ++j) {
            audio->data[i * audio->length + j] = 0.0;
        }
    }

    //printf("exiting realloc\n");
    return -(audio->data == NULL);
}

int32_t chaudio_audio_realloc_audio(audio_t * audio, audio_t tofit) {
    return chaudio_audio_realloc(audio, tofit.length, tofit.channels, tofit.sample_rate);
}


int32_t chaudio_audio_free(audio_t * audio) {
    if (audio == NULL) {
        return -1;
    }

    if (audio->data != NULL) {
        free(audio->data);
        audio->data = NULL;
    }

    audio->length = 0;
    audio->channels = 0;
    audio->sample_rate = CHAUDIO_DEFAULT_SAMPLE_RATE;

    return 0;
}

double clamp(double x, double mn, double mx) {
    if (x < mn) return mn;
    if (x > mx) return mx;
    return x;
}

int32_t chaudio_audio_output_wav_fp(FILE * fp, audio_t audio, int32_t format) {

    wav_header_t wav_header;

    memcpy(wav_header.riff, "RIFF", 4);
    memcpy(wav_header.wave, "WAVE", 4);
    memcpy(wav_header.format_chunk_marker, "fmt ", 4);
    memcpy(wav_header.data_chunk_header, "data", 4);

    wav_header.format_length = 16;

    wav_header.format_type = 1; //1 is PCM, 3 is IEEE floating point

    wav_header.channels = audio.channels;
    wav_header.sample_rate = audio.sample_rate;

    int32_t bps = 0;
    if (format == CHAUDIO_WAVFMT_8I) {
        bps = 8;
    } else if (format == CHAUDIO_WAVFMT_16I) {
        bps = 16;
    } else if (format == CHAUDIO_WAVFMT_24I) {
        bps = 24;
    } else if (format == CHAUDIO_WAVFMT_32I) {
        bps = 32;
    } else {
        printf("unrecognized WAVFMT\n");
        return -2;
    }

    wav_header.byte_rate = audio.sample_rate * audio.channels * bps / 8;
    wav_header.block_align = audio.channels * bps / 8;
    wav_header.bits_per_sample = bps;

    int32_t data_size = audio.length * audio.channels * bps / 8;
    
    wav_header.data_size = data_size;
    wav_header.file_size = data_size + sizeof(wav_header);

    void * wav_file_result = (void *)malloc(data_size);

    int i, j;
    if (format == CHAUDIO_WAVFMT_8I) {
        int8_t * output = (int8_t *)wav_file_result;
        for (i = 0; i < audio.length; ++i) {
            for (j = 0; j < audio.channels; ++j) {
                output[i * audio.channels + j] = (int8_t)floor(clamp(audio.data[i + j * audio.length], -1.0, 1.0) * 127.0);
            }
        }

    } else if (format == CHAUDIO_WAVFMT_16I) {
        int16_t * output = (int16_t *)wav_file_result;
        for (i = 0; i < audio.length; ++i) {
            for (j = 0; j < audio.channels; ++j) {
                output[i * audio.channels + j] = (int16_t)floor(clamp(audio.data[i + j * audio.length], -1.0, 1.0) * 32767.0);
            }
        }
    } else if (format == CHAUDIO_WAVFMT_24I) {
        int8_t * packed_output = (int8_t *)wav_file_result;
        int32_t packed_tmp = 0;

        int out_idx;
        for (i = 0; i < audio.length; ++i) {
            for (j = 0; j < audio.channels; ++j) {
                packed_tmp = (int32_t)floor(clamp(audio.data[i + j * audio.length], -1.0, 1.0) * 8388607.0);
                out_idx = i * audio.channels + j;
                packed_output[3 * out_idx + 0] = packed_tmp & 0xFF;
                packed_output[3 * out_idx + 1] = (packed_tmp >> 8) & 0xFF;
                packed_output[3 * out_idx + 2] = (packed_tmp >> 16) & 0xFF;
            }
        }
    } else if (format == CHAUDIO_WAVFMT_32I) {
        int32_t * output = (int32_t *)wav_file_result;
        for (i = 0; i < audio.length; ++i) {
            for (j = 0; j < audio.channels; ++j) {
                output[i * audio.channels + j] = (int32_t)floor(clamp(audio.data[i + j * audio.length], -1.0, 1.0) * 2147483647.0);
            }
        }
    }

    fwrite(&wav_header, 1, sizeof(wav_header), fp);
    fwrite(wav_file_result, 1, wav_header.data_size, fp);

    // free array
    free(wav_file_result);

    return 0;
}

int32_t chaudio_audio_output_wav(char * file_path, audio_t audio, int32_t format) {
    if (file_path == NULL) {
        printf("'file_path' for output was NULL, writing failed\n");
        return -1;
    }    

    FILE * fp = fopen(file_path, "w");

    int32_t res = chaudio_audio_output_wav_fp(fp, audio, format);

    fclose(fp);

    return res;
}





