
#include "chaudio.h"

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

int chaudio_init() {

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

// the dl loading init value
bool has_made_chaudio_dl = false;
chaudio_dl_init_t _chaudio_dl_init;

chaudio_dl_init_t chaudio_dl_init() {
    if (!has_made_chaudio_dl) {
        _chaudio_dl_init = (chaudio_dl_init_t) { 

            .chaudio_audio_create = chaudio_audio_create,
            .chaudio_audio_create_wav = chaudio_audio_create_wav,
            .chaudio_pad = chaudio_pad,

            .chaudio_audio_free = chaudio_audio_free,
            .chaudio_paraminterface_create = chaudio_paraminterface_create,

            .chaudio_plugin_create = chaudio_plugin_create,
            .chaudio_generator_create = chaudio_generator_create,
            .chaudio_output_create = chaudio_output_create,
            .chaudio_time = chaudio_time,
            .chaudio_audio_output_wav = chaudio_audio_output_wav,
            .chaudio_audio_output_wav_fp = chaudio_audio_output_wav_fp,
            .chaudio_read_wav_samples = chaudio_read_wav_samples,


            .chfft_alloc = chfft_alloc,
            .chfft_realloc = chfft_realloc,
            .chfft_free = chfft_free,
            .chfft_fft = chfft_fft,
            .chfft_ifft = chfft_ifft
            
        };
        has_made_chaudio_dl = true;
    }

    return _chaudio_dl_init;
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

        #ifdef HAVE_JACK
        sprintf(_build_res, "%s (built with JACK)", _build_res);
        #endif

    }

    return _build_res;
}


int chaudio_read_wav_samples(char * wav_file, double ** outputs, int * length, int * channels, int * sample_rate) {
    
    FILE * fp = fopen(wav_file, "r");

    if (fp == NULL) {
        printf("can't read wave samples\n");
        return 1;
    }

    wav_header_t wav_header;
    fread(&wav_header, 1, sizeof(wav_header), fp);

    *channels = (int)wav_header.channels;
    *sample_rate = (int)wav_header.sample_rate;
    *length = (int)((8 * wav_header.data_size) / (wav_header.channels * wav_header.bits_per_sample));

    int32_t bps = wav_header.bits_per_sample;

    *outputs = realloc(*outputs, sizeof(double) * (*length) * (*channels));

    void * smp = malloc(wav_header.data_size);
    fread(smp, 1, wav_header.data_size, fp);

    int i;

    if (bps == 8) {
        for (i = 0; i < *length * *channels; ++i) (*outputs)[i] = (double)((int8_t *)smp)[i] / 127.0;
    } else if (bps == 16) {
        for (i = 0; i < (*length) * (*channels); ++i) {
            (*outputs)[i] = (double)(((int16_t *)smp)[i]) / 32768.0;
        }
    } else if (bps == 24) {
        for (i = 0; i < *length * *channels; ++i) {
            int8_t * smp8i = (int8_t *)smp;
            (*outputs)[i] = (double)(smp8i[3*i] + smp8i[3*i + 1] * 256 + smp8i[3*i + 2] * 256 * 256) / 8388608.0;
        }
    } else if (bps == 32) {
        for (i = 0; i < *length * *channels; ++i) {
            (*outputs)[i] = 0.0;
        }
    } else {
        printf("unknown bps: %d\n", bps);
        return 1;
    }

    return 0;
}

// initialization stuff
audio_t chaudio_audio_create(int length, int channels, int sample_rate) {
    audio_t audio;

    audio.length = length;
    audio.channels = channels;
    audio.sample_rate = sample_rate;

    // NULL so realloc works
    if (channels == 0 || length == 0) audio.data = NULL;
    else {
        audio.data = (double *)malloc(sizeof(double) * audio.length * audio.channels);
        if (audio.data == NULL) {
            printf("OUT OF MEMORY\n");
            exit(1);
        }
    }

    int i;
    for (i = 0; i < audio.length * audio.channels; ++i) {
        audio.data[i] = 0.0;
    }
    return audio;
}

audio_t chaudio_audio_create_nothing() {
    return chaudio_audio_create(0, 0, CHAUDIO_DEFAULT_SAMPLE_RATE);
}

audio_t chaudio_audio_create_audio(audio_t from) {
    audio_t audio;

    audio.length = from.length;
    audio.channels = from.channels;
    audio.sample_rate = from.sample_rate;

    audio.data = malloc(sizeof(double) * audio.length * audio.channels);
    
    int i;
    for (i = 0; i < audio.length * audio.channels; ++i) {
        audio.data[i] = from.data[i];
    }

    return audio;
}

// need to read in file
audio_t chaudio_audio_create_wav(char * file_path) {
    audio_t r;
    r.data = NULL;

    int x = chaudio_read_wav_samples(file_path, &r.data, &r.length, &r.channels, &r.sample_rate);

    return r;
}


int chaudio_audio_realloc(audio_t * audio, int new_length, int new_channels, int new_sample_rate) {
    //printf("entering \n");
    if (audio == NULL) {
        return -1;
    }

    int old_length = audio->length;
    int old_channels = audio->channels;

    //printf(" setting members\n");
    if (new_length != 0) audio->length = new_length;
    if (new_channels != 0) audio->channels = new_channels;
    if (new_sample_rate != 0) audio->sample_rate = new_sample_rate;

    //printf(" calling func\n");
    audio->data = (double *)realloc((void *)audio->data, sizeof(double) * audio->channels * audio->length);

    int i, j;


    // first cover all appended values to pre-existing channels
    for (i = old_length; i < audio->length; ++i) {
        for (j = 0; j < old_channels; ++j) {
            audio->data[audio->channels * i + j] = 0.0;
        }
    }
    // fill all new channels with 0.0's
    for (i = 0; i < audio->length; ++i) {
        for (j = old_channels; j < audio->channels; ++j) {
            audio->data[audio->channels * i + j] = 0.0;
        }
    }

    //printf("exiting realloc\n");
    return -(audio->data == NULL);
}

int chaudio_audio_realloc_audio(audio_t * audio, audio_t tofit) {
    return chaudio_audio_realloc(audio, tofit.length, tofit.channels, tofit.sample_rate);
}


int chaudio_audio_free(audio_t * audio) {
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

int chaudio_audio_output_wav_fp(FILE * fp, audio_t audio, int format) {

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

    wav_header.channels = (uint16_t)audio.channels;
    
    wav_header.sample_rate = (uint32_t)audio.sample_rate;

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

    wav_header.byte_rate = (uint32_t)(audio.sample_rate * audio.channels * bps / 8);
    wav_header.block_align = (uint16_t)(audio.channels * bps / 8);
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
                output[i * audio.channels + j] = (int8_t)floor(clamp(audio.data[audio.channels * i + j], -1.0, 1.0) * 127.0);
            }
        }

    } else if (format == CHAUDIO_WAVFMT_16I) {
        int16_t * output = (int16_t *)wav_file_result;
        for (i = 0; i < audio.length; ++i) {
            for (j = 0; j < audio.channels; ++j) {
                output[i * audio.channels + j] = (int16_t)floor(clamp(audio.data[audio.channels * i + j], -1.0, 1.0) * 32767.0);
            }
        }
    } else if (format == CHAUDIO_WAVFMT_24I) {
        int8_t * packed_output = (int8_t *)wav_file_result;
        int32_t packed_tmp = 0;

        int out_idx;
        for (i = 0; i < audio.length; ++i) {
            for (j = 0; j < audio.channels; ++j) {
                packed_tmp = (int32_t)floor(clamp(audio.data[audio.channels * i + j], -1.0, 1.0) * 8388607.0);
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
                output[audio.channels * i + j] = (int32_t)floor(clamp(audio.data[audio.channels * i + j], -1.0, 1.0) * 2147483647.0);
            }
        }
    }

    fwrite(&wav_header, 1, sizeof(wav_header), fp);
    fwrite(wav_file_result, 1, wav_header.data_size, fp);

    // free array
    free(wav_file_result);

    return 0;
}

int chaudio_audio_output_wav(char * file_path, audio_t audio, int format) {
    if (file_path == NULL) {
        printf("'file_path' for output was NULL, writing failed\n");
        return -1;
    }    

    FILE * fp = fopen(file_path, "w");

    int res = chaudio_audio_output_wav_fp(fp, audio, format);

    fclose(fp);

    return res;
}





