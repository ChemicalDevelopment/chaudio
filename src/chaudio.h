/*

chaudio.h - common definitions

*/


#ifndef __CHAUDIO_H__
#define __CHAUDIO_H__

#include <stdint.h>


// defaults
#define CHAUDIO_DEFAULT_SAMPLE_RATE 44100



// max size a chaudio error would be
#define CHAUDIO_MAX_ERROR_LENGTH 1024

char * chaudio_cur_error;

/*


double floating points values are used for all internal calculations

*/

/*

Here are all available formats for wave file output

*/


#define CHAUDIO_WAVFMT_8I     0x0001
#define CHAUDIO_WAVFMT_16I    0x0002
#define CHAUDIO_WAVFMT_24I    0x0003
#define CHAUDIO_WAVFMT_32I    0x0004

//#define CHAUDIO_WAVFMT_32F    0x0005



typedef struct audio_t {

    // how many channels are there? 1 is mono, 2 is stereo, its probably one of those two 99% of the time
    // but it can serve as a mixer
    uint16_t channels;

    // how many samples are there in each channel (so total number of samples = channels * length)
    uint32_t length;

    // sample rate of the samples
    uint32_t sample_rate;

    // points to the data
    // has sizeof(double) * length * channels bytes allocated to it
    // data[0], data[1]...data[length-1] is channel 0,
    // data[length], data[length+1]...data[2*length-1] is channel 1, 
    // etc
    double * data;


} audio_t;

// basic functions
// int32_t return types are normally for errors, 0 is no error, + is status, and - is critical
// so to check if it was successful, check (func() >= 0)


int32_t chaudio_init();

// set the error (should only be used internally)
// the function that calls this should free their error message
void chaudio_set_error(char * error_txt);

// gets most recent error. The user is responsible for freeing this
char * chaudio_get_error();


// ALL audio_t VARIABLES ARE UNDEFINED BEFORE A METHOD THAT STARTS WITH `chaudio_create_` has been called on them. Do not use them before that


// creates audio (blanks it to 0.0's)
int32_t chaudio_create_audio(audio_t * audio, uint16_t channels, uint32_t length, uint32_t sample_rate);

// copies the audio, creating a new object
// audio should be not created yet (if it is, use chaudio_destroy_audio(audio) then call this function)
int32_t chaudio_create_audio_from_audio(audio_t * audio, audio_t from);


// creates an audio object from wave file contents
int32_t chaudio_create_audio_from_wav_file(audio_t * audio, char * file_path);


// reallocs memory to hold new_length
int32_t chaudio_resize_audio(audio_t * audio, uint32_t new_length);


int32_t chaudio_realloc(audio_t * audio, uint16_t new_channels, uint32_t new_length);

// destroys/frees the audio data
int32_t chaudio_destroy_audio(audio_t * audio);


// output to wave file
// format is CHAUDIO_WAVFMT_* macros
int32_t chaudio_to_wav_file(char * file_path, audio_t audio, int32_t format);


// things to include
#include "ch_util.h"

#endif


