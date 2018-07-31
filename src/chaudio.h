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
#include <math.h>    // used for math constants, functions used in macros


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

constants - values that don't change and are useful "points" of interest

*/


// this is what should be returned if an error occurred, indicating something went wrong
#define AUDIO_NULL ((audio_t){ .length = -1, .channels = -1, .sample_rate = -1, .data = NULL })


#define CHAUDIO_PLUGIN_NULL ((chaudio_plugin_t) { .name = NULL, .init = NULL, .process = NULL, .free = NULL })

// call this as the `db` argument for anything with gain to get a silent signal
#define CHAUDIO_GAIN_SILENT (-(INFINITY))

// this will do nothing to the signal
#define CHAUDIO_GAIN_NOTHING (0.0)

// just the definitions of seconds and milliseconds
#define S_PER_MS (0.001)
#define MS_PER_S (1000.0)

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


/*

flag specifiers - enum-like declarations to pass

*/

/* OBJTYPE : describes the internal data storage of the chdict_param



*/

#define CHAUDIO_OBJTYPE_DOUBLE   0x0001 /* if this is the type, use dictobj.val.dval */
#define CHAUDIO_OBJTYPE_INT      0x0002 /* if this is the type, use dictobj.val.ival */
#define CHAUDIO_OBJTYPE_STRING   0x0003 /* if this is the type, use dictobj.val.sval */
#define CHAUDIO_OBJTYPE_AUDIO    0x0004 /* if this is the type, use dictobj.val.aval */
#define CHAUDIO_OBJTYPE_ANY      0x0005 /* if this is the type, use dictobj.val.pval */

#define CHAUDIO_OBJTYPE_NOTFOUND 0x0101 /* if this is the type, the dictionary didn't have an entry (and dictobj.val.pval will be set to `NULL`) */



/* WAVEFORM : describes different kind of common waveforms




*/

#define CHAUDIO_WAVEFORM_SIN     0x0001
#define CHAUDIO_WAVEFORM_SQUARE  0x0002
#define CHAUDIO_WAVEFORM_NOISE   0x0101

/* SCALE : describes mathematical relationships in terms of growth, etc

This is mainly used for plugin parameters to decide how to display them

*/

#define CHAUDIO_SCALE_LINEAR 0x00 /* linear, i.e. y=ax+b */
#define CHAUDIO_SCALE_LOG 0x01 /* logarithmic, i.e. y=a*log(x)+b */
#define CHAUDIO_SCALE_EXP 0x02 /* exponential, i.e. y=a*b^x+c */



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



// parameter info
typedef struct _chparam_s {

    double minimum, maximum;

    // see PARAM_SCALE_* macros
    int32_t scale;

    // false if there is no min/max/scale
    int32_t is_applied;

} chparam_t;


// should return a pointer to some structure type that is used internally for the project.
// should not return NULL (unless a failure has occured)
// dict may be NULL!
// if not, cast to chdict_t *
typedef void * (*chaudio_PluginInit)(int32_t channels, int32_t sample_rate);

// plugin_data is the same pointer created by the ch_PluginInit function
// returns status code (0 = sucess)
// 'in' and 'out' are both of length N * channels,
// they are stored sample wise, so LRLRLRLR data for stereo
// there are N samples for each channel
// dictionary may be NULL!
// if not, cast to chdict_t *
typedef int32_t (*chaudio_PluginProcess)(void * plugin_data, double * in, double * out, int32_t N);

// sets a parameter as a double
typedef int32_t (*chaudio_PluginSetDouble)(void * plugin_data, char * key, double val);

// just the de-initializer
typedef int32_t (*chaudio_PluginFree)(void * plugin_data);

/* chaudio_plugin_t - a plugin structure. Has input and output capabilities, useful for real time audio processing */
typedef struct _chaudio_plugin_s {

    char * name;

    chaudio_PluginInit init;
    chaudio_PluginProcess process;
    chaudio_PluginSetDouble set_double;
    chaudio_PluginFree free;

    void * plugin_data;

    uint32_t channels, sample_rate;

    // in/out variables
    double * in, * out;

} chaudio_plugin_t;

/* chaudio_pipeline_t - multiple plugins chained together */
typedef struct _chaudio_pipeline_s {

    int plugins_len;
    chaudio_plugin_t * plugins;

} chaudio_pipeline_t;


typedef struct _chaudioplugin_init_s {

    chaudio_plugin_t (*chaudio_plugin_create)(char * name, chaudio_PluginInit _init, chaudio_PluginProcess _process, chaudio_PluginSetDouble _set_double, chaudio_PluginFree _free);

    double (*chaudio_time)();

} chaudioplugin_init_t;


/*

other header files for chaudio library

*/


#ifndef IS_CHAUDIO_PLUGIN
// only define functions if it isn't a plugin (because the plugin use passed parameters through the plugin interface)

#include "chaudiofunctions.h" // defines all (public) methods implemented by chaudio

#endif

#endif


