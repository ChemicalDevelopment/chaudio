/*

chaudiofunctions.h -- definitions of all common chaudio operations

Do not include this directly; using `#include <chaudio.h>` should implicitly handle function declarations

*/

#ifndef __CHAUDIOFUNCTIONS_H__
#define __CHAUDIOFUNCTIONS_H__

/* general notes

  * functions returning an `int32_t`, unless otherwise specified, return a status code, 0 indiciating no error, >0 indicating a warning (such that an unusual situation was requested, or something was wrong) but that the core operation was completed in some fastion, and <0 indicating that a critical error has occured and that variables altered during the transformation do not neccessarily reflect the documentation (for instance, if a size was requested and the system does not have enough RAM to allocate that much memory). In sum, as long as the function returned >= 0, the result is generally safe (although may not be exactly as you expect, but if <0, something that may cause the program to crash if you try and use the result.

*/


/**

TODO: decide if there should be a chaudio_init() method at all? 

*/
int32_t chaudio_init();


// return the time since the epoch if `chaudio_init()` has not been called, otherwise, the amount of elapsed time since `chaudio_init()` was called.
double chaudio_time();

// return the dl_init values used for initializing generators and plugins
chaudio_dl_init_t chaudio_dl_init();


// returns info about when/what chaudio was built, as a string. 
// Do not free the result
char * chaudio_get_build_info();


/*

non-audio_t utilities (for general usage)

*/

// reads wave samples into interlaced buffer
int32_t chaudio_read_wav_samples(char * wav_file, double ** outputs, int64_t * length, int32_t * channels, int32_t * sample_rate);

/*

creation routines (these create and allocate memory (i.e. can create memory leaks)!)

*/

// creates a silent (i.e. all samples == 0.0) audio_t with the specified values
audio_t chaudio_audio_create(int64_t length, int32_t channels, int32_t sample_rate);

// creates an audio object that has length=0, channels=0, and default sample_rate, that can be used and realloced in the future. This is good for creating result buffers that you don't know the size of yet
audio_t chaudio_audio_create_nothing();


// allocate space for and creates a copy of `from`, and returns it. The memory is a newly allocated copy; it is not aliased to `from`'s data, so you are free to use `chaudio_free(&from)` afterwards and not affect the result of this result
audio_t chaudio_audio_create_audio(audio_t from);


// allocate and create audio from an IO stream that is wave file contents (includes the WAVE header data, see `chaudio.c` for a definition of this structure). `fp` is not closed, and can be `stdin` to use like this (bash): `$ cat x.wav | my_program`
audio_t chaudio_audio_create_wav_fp(FILE * fp);


// allocated and create audio from a wav file with a path on disk indicated by the `file_path`
audio_t chaudio_audio_create_wav(char * file_path);


/*

reallocation routines

*/


// reallocs memory to hold new_length of new_channels
// sets any new memory (if any) to zeros
// if any parameters are 0, they are assumed to be the pre-existing ones
// new_sample_rate does nothing, just there for conveniently setting it

// reallocates memory to hold at least new_length, new_channels data, and sets all  newly allocated samples (if requesting more than previously) to 0.0. If any of the new attributes (length, channels, or sample rate) are 0, then they are not changed from `*audio`'s corresponding attribute is. This makes it useful, for instance, when updating just the length by doing `chaudio_audio_realloc(&audio, LENGTH, 0, 0)`
int32_t chaudio_audio_realloc(audio_t * audio, int64_t new_length, int32_t new_channels, int32_t new_sample_rate);

// reallocates `audio` to fit all the data in `tofit`, but does **not** copy `tofit`'s data. It zeros this data. For that use case, use `chaudio_copy(&audio, tofit)`
int32_t chaudio_audio_realloc_audio(audio_t * audio, audio_t tofit);


/*

free-ing routines

*/

// free()'s the internal buffer used by `*audio`, and sets all parameters to 0, except the sample rate, which is set to CHAUDIO_DEFAULT_SAMPLE_RATE. Note that after this, it is ok to use `chaudio_audio_realloc()` on `audio` without fear of memory leaks.
int32_t chaudio_audio_free(audio_t * audio);


/*

output functions/routines

*/

// writes the data of `audio` to the IO stream `fp` in WAVE file format, with specifically the `format` option (which is one of the CHAUDIO_WAVFMT_* macro values, see `chaudio.h`)
int32_t chaudio_audio_output_wav_fp(FILE * fp, audio_t audio, int32_t format);

// writes the data of `audio` out to disk in WAVE file format, with specifically the `format` option (which is one of the CHAUDIO_WAVFMT_* macro values, see `chaudio.h`). This function will overwrite the file at `file_path` if it exists and is not a directory (otherwise an error code will be returned > 0)
int32_t chaudio_audio_output_wav(char * file_path, audio_t audio, int32_t format);


/*

chaudio utilities

notes:

  * all of these functions that return an `audio_t` and also have the last parameter as `audio_t * output` are nullable; You can call with `output==NULL` and the result will be created instead of put into `*audio`. This makes it useful to have these routines auto-allocate memory. If called with `output==NULL`, you are responsible for freeing that result. 


the following two examples are equal (assuming `a` is a valid audio object):

  audio_t b = chaudio_resample(a, RATE, NULL);
  // another result is allocated, and the other is never freed. This is wrong. Please call `chaudio_free(&b)` between these two calls
  b = chaudio_resample(a, RATE, NULL);

  and
  
  audio_t b = chaudio_create_nothing();
  chaudio_resample(a, RATE, &b);
  // `b` is realloced and ensured to store the result (and it already has, so nothing changes). This is more efficient if you are repeatedly calling the same functions into a buffer
  chaudio_resample(a, RATE, &b);


*/

// returns the duration (in seconds) of `audio`
double chaudio_audio_duration(audio_t audio);

// copies (and sets all attributes) from `input`
audio_t chaudio_copy(audio_t input, audio_t * output);

// resamples (using default linear interpolation) from input
audio_t chaudio_resample(audio_t input, int64_t new_sample_rate, audio_t * output);

// creates audio from input that results in the same length, but only one channel. This is done by averaging all the channels in input
audio_t chaudio_mix_to_mono(audio_t input, audio_t * output);

// returns audio that is input multiplied by a factor so that abs(RESULT) <= 1.0 for all values
audio_t chaudio_normalize(audio_t input, audio_t * output);

// returns audio that is multiplied by the gain coefficient (see macro GAIN_COEF in chaudio.h). Gain is a exp-scale measurement. The multiplication factor increases exponentially as db increases linearly. Use CHAUDIO_GAIN_SILENT
audio_t chaudio_gain(audio_t input, double db, audio_t * output);

// adjusts to a new length
audio_t chaudio_adjust_length(audio_t input, int64_t to_length, audio_t * output);

// pad, add extra zeros
audio_t chaudio_pad(audio_t input, int64_t num_zeros, audio_t * output);

// appends them together
audio_t chaudio_append(audio_t input_A, audio_t input_B, audio_t * output);



/*

signal generation

*/

// TODO: rewrite this to make more sense
void chaudio_signal_generate(audio_t * output, int32_t waveform, double hz, double phase_offset);


/*

plugin interface

*/

// this is used by generators, plugins, and outputs
chaudio_paraminterface_t chaudio_paraminterface_create(chaudio_SetDouble set_double, chaudio_SetInt set_int, chaudio_SetString set_string, chaudio_SetAudio set_audio);


// create a plugin, essentially an initialization routine
chaudio_plugin_t chaudio_plugin_create(char * name, chaudio_PluginInit _init, chaudio_PluginProcess _process, chaudio_PluginFree _free, chaudio_paraminterface_t params);

chaudio_plugin_t chaudio_plugin_create_plugin(chaudio_plugin_t plg);

// this calls the supplied .init method passed in, allows for the plugin to initialize data and store channels/sample_rate
void chaudio_plugin_init(chaudio_plugin_t * plugin, int32_t channels, int32_t sample_rate);

// computes a new buffer of transformed audio. Stores into `output` if it isn't NULL, otherwise returns a newly allocated result (which you should free). Call this function with small chunks in a loop to process a stream in real time
audio_t chaudio_plugin_transform(chaudio_plugin_t * plugin, audio_t from, int32_t bufsize, audio_t * output);

// call the plugin's free function, so that the plugin author's memory freeing and finishing routine can run
int32_t chaudio_plugin_free(chaudio_plugin_t * plugin);

// load from .so on linux, .dylib on macos, .dll on windows, must be a resolvable path to it (this method doesn't search any other directories than normally opening file)
chaudio_plugin_t chaudio_plugin_load(char * file_name);


// generator api

chaudio_generator_t chaudio_generator_create(char * name, chaudio_GeneratorInit _init, chaudio_GeneratorGenerate _generate, chaudio_GeneratorFree _free, chaudio_paraminterface_t params);

int32_t chaudio_generator_init(chaudio_generator_t * gen, int32_t channels, int32_t sample_rate);

// generates and stores into gen->out
int32_t chaudio_generator_generate(chaudio_generator_t * gen, int32_t bufsize);

int32_t chaudio_generator_free(chaudio_generator_t * gen);

// dynamic loading
chaudio_generator_t chaudio_generator_load(char * file_name);



chaudio_output_t chaudio_output_create(char * name, chaudio_OutputInit _init, chaudio_OutputDump _dump, chaudio_OutputFree _free, chaudio_paraminterface_t params);

int32_t chaudio_output_init(chaudio_output_t * output, int32_t channels, int32_t sample_rate);
int32_t chaudio_output_dump(chaudio_output_t * output, double * in, int32_t N);

int32_t chaudio_output_free(chaudio_output_t * output);

chaudio_output_t chaudio_output_load(char * file_name);


// pipeline extension

chaudio_pipeline_t chaudio_pipeline_create(int32_t channels, int32_t sample_rate);

void chaudio_pipeline_init(chaudio_pipeline_t * pipeline);


void chaudio_pipeline_add(chaudio_pipeline_t * pipeline, chaudio_plugin_t plugin);


// works like iterated on chaudio_plugin_transform
audio_t chaudio_pipeline_transform(chaudio_pipeline_t * pipeline, audio_t from, int32_t bufsize, audio_t * output);

// run indefinetely (if stop_func == NULL), or until stop_func() == true
void chaudio_pipeline_runstream(chaudio_pipeline_t * pipeline, int32_t bufsize, double audio_length, chaudio_IsFinished stop_func);

void chaudio_pipeline_free(chaudio_pipeline_t * pipeline);


#ifdef HAVE_PORTAUDIO

// else give an error or something
void chaudio_portaudio_realtime_process(chaudio_pipeline_t * pipeline, int32_t bufsize);

#endif



#endif

