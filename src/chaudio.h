/*

chaudio.h -- the header file for the Chemical Development audio library

Please see https://github.com/ChemicalDevelopment/chaudio for full source



Authors:

  * Cade Brown <cade@chemicaldevelopment.us>

*/


#ifndef __CHAUDIO_H__
#define __CHAUDIO_H__



/* only neccessary headers */
#include <stdint.h>  // used for int sizes (for specific and guaranteed alignment)
#include <stdio.h>   // used for FILE * streams
#include <stdlib.h>  // headers
#include <math.h>    // used for math constants, functions used in macros
#include <string.h>
#include <stdbool.h>
#include <complex.h>


#ifndef M_PI
#define M_PI 3.141592653589793238462643383279502884
#endif


/*

defaults - values that don't change but are subjective

*/

// this is the most common sample rate, 
#define CHAUDIO_DEFAULT_SAMPLE_RATE (44100)

// a good buffer size to use for processing data
#define CHAUDIO_DEFAULT_BUFFER_SIZE (256)

/*

flags/indicators

*/

// return codes
#define CHAUDIO_CONTINUE    (0x0000)

// return this if a generator has stopped generating stuff (like the end of a wave file)
#define CHAUDIO_FINISHED    (0x1001)


/*

constants - values that don't change and are useful "points" of interest

*/


// this is what should be returned if an error occurred, indicating something went wrong
#define AUDIO_NULL ((audio_t){ .length = -1, .channels = -1, .sample_rate = -1, .data = NULL })


// macro to check if generator is valid or not
#define CHAUDIO_GENERATOR_ISVALID(x) ((x).name != NULL)

// macro to check if a plugin is valid or not
#define CHAUDIO_PLUGIN_ISVALID(x) ((x).name != NULL)
#define CHAUDIO_OUTPUT_ISVALID(x) ((x).name != NULL)


// call this as the `db` argument for anything with gain to get a silent signal
#define CHAUDIO_GAIN_SILENT (-(INFINITY))

// this will do nothing to the signal
#define CHAUDIO_GAIN_NOTHING (0.0)

// just the definitions of seconds and milliseconds
#define S_PER_MS (0.001)
#define MS_PER_S (1000.0)

// this is for looped indexing, specifically for circular buffers
#define CIRCLEBUF_IDX(i, N) ((((i) % (N)) + N) % (N))

// function to transform gain (in decibels) to a coefficient to multiply a signal by. Gain is exponential scaled, which means as `db` increases linearly, `GAIN_COEF(db)` increases exponentially
#define GAIN_COEF(db) (pow(10.0, (db) / 20.0))

// returns the `phase` as how many cycles the corresponding degree or radian measurement is. So, 180 degrees is 0.5 out of phase, 360 is 1.0 out of phase (which on unchanging waveforms is the same as 0 degrees). This is the proportion of a full revolution
#define PHASE_DEGREES(n) ((n) / 360.0)
#define PHASE_RADIANS(n) ((n) / (2 * M_PI));

/*

utilities - macros that tell useful things about the audio data

*/

// is true if the audio is a mono-channel recording (just one channel)
#define CHAUDIO_IS_MONO(au) ((bool)((au).channels == 1))

// is true if the audio is a stereo-channel recording (two channels, L and R)
#define CHAUDIO_IS_STEREO(au) ((bool)((au).channels == 2))

// returns the index of the sample of channel `chan` and index `i`
#define CHAUDIO_SAMPLE_INDEX(aud, chan, i) ((aud).channels * (i) + (chan))

/* WAVEFORM : describes different kind of common waveforms




*/

#define CHAUDIO_WAVEFORM_SIN     0x0001
#define CHAUDIO_WAVEFORM_SQUARE  0x0002
#define CHAUDIO_WAVEFORM_NOISE   0x0101


/* WAVFMT : common WAVE file format specifiers 

max error for fixed point (all that end with 'I') is 1.0/2^bits

maximum signal ratio is the inverse gain function of 2^-bits, here's a chart:

See: https://en.wikipedia.org/wiki/Audio_bit_depth#Quantization for info (values aren't exact because our range is -1.0 to +1.0)

| bit depth | unique values | quantization error | random noise |
|         8 |           256 |      <= 0.0078125 | <= -42.13 db |
|        16 |         65536 |      <= 3.0518e-5 | <= -90.30 db |
|        24 |      16777216 |      <= 1.1921e-7 | <= -138.4 db |
|        32 |    4294967296 |      <= 4.657e-10 | <= -186.5 db |

*/


#define CHAUDIO_WAVFMT_8I     0x0001  /* 8 bit integer fixed point format */
#define CHAUDIO_WAVFMT_16I    0x0002  /* 16 bit integer fixed point format (CD quality) */
#define CHAUDIO_WAVFMT_24I    0x0003  /* 24 bit integer fixed point format (high sample library quality) */
#define CHAUDIO_WAVFMT_32I    0x0004  /* 32 bit integer fixed point format (WARNING: this is not highly supported in all programs) */

// TODO: consider writing float/double parsers for IEEE
//#define CHAUDIO_WAVFMT_32F    0x0005
//#define CHAUDIO_WAVFMT_64F    0x0006



/*

type declarations - these are all definitions programs need

*/

/* audio_t - the primary structure of chaudio, which represents a chunk of signal of a number of channels for a length */
typedef struct audio_t {

    // how many samples are there in each channel (so total number of samples = channels * length)
    
    // `length`: the number of samples that the chunk of audio is representing (each channel has this many)
    int64_t length;

    // `channels`: the number of different `channels` of audio.
    // For instance, stereo tracks are 2 channels (channel 0 is Left, channel 1 is Right). Mono is 1 channel
    int32_t channels;

    // sample rate, in samples/second. 
    // The most widely used sample rate (44100) is defined as CHAUDIO_DEFAULT_SAMPLE_RATE
    int32_t sample_rate;

    // a pointer to memory to the sample data, with memory size of at least `sizeof(double) * length* channels`
    // the data is stored as interlaced channels
    // So, for instance, data for a stereo chunk of audio with a length of 4 would look like this: 
    //   `LRLRLRLR`, and have 8 (==4 * 2) total doubles allocated.
    double * data;

} audio_t;




// a generic bool 'is_finished' function
typedef bool (*chaudio_IsFinished)();

// should return a pointer to some structure type that is used internally for the project.
// should not return NULL (unless a failure has occured)
// dict may be NULL!
// if not, cast to chdict_t *
typedef void * (*chaudio_PluginInit)(int32_t channels, int32_t sample_rate);
typedef void * (*chaudio_GeneratorInit)(int32_t channels, int32_t sample_rate);
typedef void * (*chaudio_OutputInit)(int32_t channels, int32_t sample_rate);


// _data is the same pointer created by the ch_PluginInit function
// returns status code (0 = sucess)
// 'in' and 'out' are both of length N * channels,
// they are stored sample wise, so LRLRLRLR data for stereo
// there are N samples for each channel
// dictionary may be NULL!
// if not, cast to chdict_t *
typedef int32_t (*chaudio_PluginProcess)(void * _data, double * in, double * out, int32_t N);
typedef int32_t (*chaudio_GeneratorGenerate)(void * _data, double * out, int32_t N);
typedef int32_t (*chaudio_OutputDump)(void * _data, double * in, int32_t N);


// generic set 
typedef int32_t (*chaudio_SetDouble)(void * _data, char * key, double val);
typedef int32_t (*chaudio_SetInt)(void * _data, char * key, int32_t val);
typedef int32_t (*chaudio_SetString)(void * _data, char * key, char * val);
typedef int32_t (*chaudio_SetAudio)(void * _data, char * key, audio_t val);

typedef struct chaudio_paraminterface_t {

    chaudio_SetDouble set_double;
    chaudio_SetInt set_int;
    chaudio_SetString set_string;
    chaudio_SetAudio set_audio;

} chaudio_paraminterface_t;



// just the de-initializer
typedef int32_t (*chaudio_PluginFree)(void * _data);
typedef int32_t (*chaudio_GeneratorFree)(void * _data);
typedef int32_t (*chaudio_OutputFree)(void * _data);


/* chaudio_plugin_t - a plugin structure. Has input and output capabilities, useful for real time audio processing */
typedef struct _chaudio_plugin_s {

    char * name;

    chaudio_PluginInit init;
    chaudio_PluginProcess process;
    chaudio_PluginFree free;

    chaudio_paraminterface_t params;

    void * plugin_data;

    int32_t channels, sample_rate;

    // in/out variables
    double * in, * out;

} chaudio_plugin_t;


/* chaudio_generator_t - an audio source essentially */
typedef struct _chaudio_generator_s {

    char * name;

    // user data structure
    void * generator_data;

    chaudio_GeneratorInit init;
    chaudio_GeneratorGenerate generate;
    chaudio_GeneratorFree free;

    chaudio_paraminterface_t params;

    int32_t channels, sample_rate;

    // how many samples are currently stored
    int32_t N;
    
    double * out;

} chaudio_generator_t;


// output (can be wav file, speaker, etc)
typedef struct _chaudio_output_s {

    char * name;

    void * output_data;

    chaudio_OutputInit init;
    chaudio_OutputDump dump;
    chaudio_OutputFree free;

    chaudio_paraminterface_t params;

    int32_t channels, sample_rate;

} chaudio_output_t;


/* chaudio_pipeline_t - multiple plugins chained together */
typedef struct _chaudio_pipeline_s {

    // can be NULL, in that case use 0.0s
    chaudio_generator_t * generator;

    chaudio_output_t * output;

    // should be uniform across the plugins
    int32_t channels, sample_rate;

    int plugins_len;
    chaudio_plugin_t * plugins;


    // swap buffers
    double * in, * out;

} chaudio_pipeline_t;




// for FFTs
typedef struct _chfft_plan_s {

    int N;
    bool is_inverse;

    void * _internal;

} chfft_plan_t;



typedef struct _chaudio_dl_init_s {


    int32_t (*chaudio_read_wav_samples)(char * wav_file, double ** outputs, int64_t * length, int32_t * channels, int32_t * sample_rate);

    chaudio_paraminterface_t (*chaudio_paraminterface_create)(chaudio_SetDouble set_double, chaudio_SetInt set_int, chaudio_SetString set_string, chaudio_SetAudio set_audio);

    chaudio_plugin_t (*chaudio_plugin_create)(char * name, chaudio_PluginInit _init, chaudio_PluginProcess _process, chaudio_PluginFree _free, chaudio_paraminterface_t params);

    chaudio_generator_t (*chaudio_generator_create)(char * name, chaudio_GeneratorInit _init, chaudio_GeneratorGenerate _generate, chaudio_GeneratorFree _free, chaudio_paraminterface_t params);

    chaudio_output_t (*chaudio_output_create)(char * name, chaudio_OutputInit _init, chaudio_OutputDump _generate, chaudio_OutputFree _free, chaudio_paraminterface_t params);


    int32_t (*chaudio_audio_output_wav_fp)(FILE * fp, audio_t audio, int32_t format);
    int32_t (*chaudio_audio_output_wav)(char * file_path, audio_t audio, int32_t format);

    double (*chaudio_time)();


    chfft_plan_t (*chfft_fft_plan)(int N);

    chfft_plan_t (*chfft_ifft_plan)(int N);

    void (*chfft_plan_free)(chfft_plan_t plan);

    void (*chfft_doplan)(double * audio_data, complex double * freq_data, chfft_plan_t plan);



} chaudio_dl_init_t;


/*

other header files for chaudio library

*/


#if !defined(IS_CHAUDIO_PLUGIN) && !defined(IS_CHAUDIO_GENERATOR) && !defined(IS_CHAUDIO_OUTPUT)
// only define functions if it isn't a plugin (because the plugin use passed parameters through the plugin interface)

#include "chaudiofunctions.h" // defines all (public) methods implemented by chaudio

#endif

#endif


