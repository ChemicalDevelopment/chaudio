
#include "chaudio.h"

#include "util.h"

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>


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


char * chaudio_cur_error = NULL;


int32_t chaudio_init() {
    chaudio_cur_error = (char *)malloc(CHAUDIO_MAX_ERROR_LENGTH+1);
    chaudio_cur_error[0] = (char)0;
}



// set the error. this is normally just used internally
void chaudio_set_error(char * error_txt) {
    int i;
    for (i = 0; i < strlen(error_txt) && i < CHAUDIO_MAX_ERROR_LENGTH; ++i) {
        chaudio_cur_error[i] = error_txt[i];
    }
    chaudio_cur_error[i] = (char)0;
}

// return the internal error state
char * chaudio_get_error() {
    return strdup(chaudio_cur_error);
}

// initialization stuff
int32_t chaudio_create_audio(audio_t * audio, uint16_t channels, uint32_t length, uint32_t sample_rate) {
    if (audio == NULL) {
        chaudio_set_error("'audio_t * audio' was NULL, creation failed");
        return -1;
    }

    audio->channels = channels;
    audio->length = length;
    audio->sample_rate = sample_rate;

    if (audio->data == NULL) {
        audio->data = (double *)malloc(sizeof(double) * audio->channels * audio->length);
        int i;
        for (i = 0; i < audio->channels * audio->length; ++i) {
            audio->data[i] = 0.0;
        }
        return 0;
    } else { // for some reason the data isn't NULL. Don't free it, because that could create segfaults. But do return a positive value so they know somethings up
        audio->data = (double *)malloc(sizeof(double) * audio->channels * audio->length);
        int i;
        for (i = 0; i < audio->channels * audio->length; ++i) {
            audio->data[i] = 0.0;
        }
        return 1;
    }
}

int32_t chaudio_create_audio_from_audio(audio_t * audio, audio_t from) {
    if (audio == NULL) {
        chaudio_set_error("'audio_t * audio' was NULL, creation failed");
        return -1;
    }

    if (from.data == NULL) {
        chaudio_set_error("'from.data' was NULL, creation as copying failed");
        return -2;
    }

    audio->channels = from.channels;
    audio->length = from.length;
    audio->sample_rate = from.sample_rate;

    
    int32_t res = 0;

    if (audio->data != NULL) {
        res = 1;
    }

    audio->data = malloc(sizeof(double) * audio->channels * audio->length);

    int i;
    for (i = 0; i < audio->channels * audio->length; ++i) {
        audio->data[i] = from.data[i];
    }

    return res;
}


// need to read in file
int32_t chaudio_create_audio_from_wav_file(audio_t * audio, char * file_path) {
    if (audio == NULL) {
        chaudio_set_error("'audio_t * audio' was NULL, creation failed");
        return -1;
    }

    // struct to store data 

    wav_header_t wave_header;

    // open the file for reading
    FILE * fp = fopen(file_path, "r");

    if (fp == NULL) {
        chaudio_set_error("opening file failed");
        return -1;
    }

    // read packed data
    fread(&wave_header, sizeof(wave_header), 1, fp);

    audio->sample_rate = wave_header.sample_rate;
    audio->channels = wave_header.channels;
    audio->length = 8 * wave_header.data_size / (wave_header.channels * wave_header.bits_per_sample);
    
    audio->data = (double *)malloc(sizeof(double) * audio->length * audio->channels); 

    void * wave_data = (void *)malloc(wave_header.data_size);

    fread(wave_data, wave_header.data_size, BUFSIZ, fp);

    // end file operations
    fclose(fp);

    int i, j;

    if (wave_header.format_type == 3) { // IEEE floating point
        if (wave_header.bits_per_sample == 8 * sizeof(float)) { // 'float' type
            float * wave_floats = (float *)wave_data;
            for (i = 0; i < audio->length; ++i) {
                for (j = 0; j < audio->channels; ++j) {
                    audio->data[audio->length * j + i] = wave_floats[audio->channels * i + j];
                }
            } 
        } else if (wave_header.bits_per_sample == 8 * sizeof(double)) { // 'double' type
            double * wave_doubles = (double *)wave_data;
            for (i = 0; i < audio->length; ++i) {
                for (j = 0; j < audio->channels; ++j) {
                    audio->data[audio->length * j + i] = wave_doubles[audio->channels * i + j];
                }
            } 
        } else {
            chaudio_set_error("unknown IEEE floating point wave bit size");
            return -1;
        }
    
    } if (wave_header.format_type == 1 || true) { //standard PCM packed fixed point, or assume all others are this
        if (wave_header.bits_per_sample == 8 * sizeof(int8_t)) {
            int8_t * wave_int8s = (int8_t *)wave_data;
            double tmp;
            for (i = 0; i < audio->length; ++i) {
                for (j = 0; j < audio->channels; ++j) {
                    tmp = (double)wave_int8s[audio->channels * i + j] / 128.0;
                    audio->data[audio->length * j + i] = tmp;
                }
            } 
        } else if (wave_header.bits_per_sample == 8 * sizeof(int16_t)) {
            int16_t * wave_int16s = (int16_t *)wave_data;
            double tmp;
            for (i = 0; i < audio->length; ++i) {
                for (j = 0; j < audio->channels; ++j) {
                    tmp = (double)wave_int16s[audio->channels * i + j] / 32768.0;
                    audio->data[audio->length * j + i] = tmp;
                }
            } 
        } else if (wave_header.bits_per_sample == 8 * 3) { // special 24 bit format
            
            int8_t * wave_int8packed = (int8_t *)wave_data;
            int64_t constructed = 0;
            double tmp;
            for (i = 0; i < audio->length; ++i) {
                for (j = 0; j < audio->channels; ++j) {
                    int pack_idx = audio->channels * i + j;
                    constructed = wave_int8packed[3 * pack_idx + 0] + (wave_int8packed[3 * pack_idx + 1] << 8) + (wave_int8packed[3 * pack_idx + 1] << 16);
                    tmp = (double)constructed / 8388608.0;
                    audio->data[audio->length * j + i] = tmp;
                }
            } 
        } else if (wave_header.bits_per_sample == 8 * sizeof(int32_t)) {
            int32_t * wave_int32s = (int32_t *)wave_data;
            double tmp;
            for (i = 0; i < audio->length; ++i) {
                for (j = 0; j < audio->channels; ++j) {
                    tmp = (double)wave_int32s[audio->channels * i + j] / 2147483648.0;
                    audio->data[audio->length * j + i] = tmp;
                }
            } 
        } 
    }
    
    free(wave_data);

    return 0;
}

int32_t chaudio_resize_audio(audio_t * audio, uint32_t new_length) {
    if (audio == NULL) {
        chaudio_set_error("'audio_t * audio' was NULL, resizing failed");
        return -1;
    }
    
    audio->length = new_length;
    audio->data = (double *)realloc((void *)audio->data, sizeof(double) * audio->length);

    if (audio->data == NULL) {
       chaudio_set_error("call to 'realloc' returned NULL"); 
       return -2;
    }

    return 0;
}


int32_t chaudio_destroy_audio(audio_t * audio) {
    if (audio == NULL) {
        chaudio_set_error("'audio_t * audio' was NULL, destroy failed");
        return -1;
    }

    int32_t res = 0;

    if (audio->data == NULL) { // for some reason, this wasn't created fully... Or they did something. In either way, don't free it
        res = 1;
    } else {
        free(audio->data);
    }

    audio->length = 0;
    
    return res;
}



int32_t chaudio_to_wav_file(char * file_path, audio_t audio, int32_t format) {
    if (file_path == NULL) {
        chaudio_set_error("'file_path' for output was NULL, writing failed");
        return -1;
    }

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
        chaudio_set_error("unrecognized WAVFMT");
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
                output[i * audio.channels + j] = (int8_t)floor(double_limit(audio.data[i + j * audio.length], -1.0, 1.0) * 128.0);
            }
        }

    } else if (format == CHAUDIO_WAVFMT_16I) {
        int16_t * output = (int16_t *)wav_file_result;
        for (i = 0; i < audio.length; ++i) {
            for (j = 0; j < audio.channels; ++j) {
                output[i * audio.channels + j] = (int16_t)floor(double_limit(audio.data[i + j * audio.length], -1.0, 1.0) * 32768.0);
            }
        }
    } else if (format == CHAUDIO_WAVFMT_24I) {
        int8_t * packed_output = (int8_t *)wav_file_result;
        int32_t packed_tmp = 0;

        int out_idx;
        for (i = 0; i < audio.length; ++i) {
            for (j = 0; j < audio.channels; ++j) {
                packed_tmp = (int32_t)floor(double_limit(audio.data[i + j * audio.length], -1.0, 1.0) * 8388608.0);
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
                output[i * audio.channels + j] = (int32_t)floor(double_limit(audio.data[i + j * audio.length], -1.0, 1.0) * 2147483648.0);
            }
        }
    }


    FILE * fp = fopen(file_path, "w");

    fwrite(&wav_header, 1, sizeof(wav_header), fp);
    fwrite(wav_file_result, 1, wav_header.data_size, fp);

    fclose(fp);


    // free array
    free(wav_file_result);
    

}





