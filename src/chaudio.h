/*

chaudio.h - common definitions

*/


#ifndef __CHAUDIO_H__
#define __CHAUDIO_H__

#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>

#include "ch_defs.h"
#include "dict.h"

// defaults

char * chaudio_cur_error;

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

// these are the NULL audio values returned if error
#define AUDIO_NULL ((audio_t){ .length = 0, .channels = 0, .sample_rate = 0, .data = NULL })


// creates audio (blanks it to 0.0's)
audio_t chaudio_audio_create(int64_t length, int32_t channels, int32_t sample_rate);
audio_t chaudio_audio_create_nothing();


// copies the audio, creating a new object
// audio should be not created yet (if it is, use chaudio_destroy_audio(audio) then call this function)
// this copies the data
audio_t chaudio_audio_create_audio(audio_t from);


// can use this on stdin
audio_t chaudio_audio_create_wav_fp(FILE * fp);


// creates an audio object from wave file contents
audio_t chaudio_audio_create_wav(char * file_path);


// reallocs memory to hold new_length of new_channels
// sets any new memory (if any) to zeros
// if any parameters are 0, they are assumed to be the pre-existing ones
// new_sample_rate does nothing, just there for conveniently setting it
int32_t chaudio_audio_realloc(audio_t * audio, int64_t new_length, int32_t new_channels, int32_t new_sample_rate);

// allocates enough to hold 'tofit'
int32_t chaudio_audio_realloc_audio(audio_t * audio, audio_t tofit);

// destroys/frees the audio data
int32_t chaudio_audio_free(audio_t * audio);


// format is CHAUDIO_WAVFMT_* macros

// output to stream
int32_t chaudio_audio_output_wav_fp(FILE * fp, audio_t audio, int32_t format);

// output to wave file
int32_t chaudio_audio_output_wav(char * file_path, audio_t audio, int32_t format);

// things to include
#include "ch_util.h"
#include "ch_plugin.h"
#include "ch_signal.h"

#endif


