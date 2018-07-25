
/*

common defines 

*/


#ifndef __CH_DEFS_H__
#define __CH_DEFS_H__


#include <stdint.h>

/*


double floating points values are used for all internal calculations

*/


// this is a safe samplerate
#define CHAUDIO_DEFAULT_SAMPLE_RATE 44100

// a good buffer size
#define CHAUDIO_DEFAULT_BUFFER_SIZE 256

// max size a chaudio error would be
#define CHAUDIO_MAX_ERROR_LENGTH 1024

#define CHAUDIO_MAX_PARAMETER_LENGTH 1024


/*

Here are all available formats for wave file output

*/


#define CHAUDIO_WAVFMT_8I     0x0001
#define CHAUDIO_WAVFMT_16I    0x0002
#define CHAUDIO_WAVFMT_24I    0x0003
#define CHAUDIO_WAVFMT_32I    0x0004

//#define CHAUDIO_WAVFMT_32F    0x0005


// chunk of audio data
typedef struct audio_t {

    // how many samples are there in each channel (so total number of samples = channels * length)
    int64_t length;

    // how many channels are there? 1 is mono, 2 is stereo, its probably one of those two 99% of the time
    // but it can serve as a mixer
    int32_t channels;

    // sample rate of the samples
    int32_t sample_rate;

    // points to the data
    // has sizeof(double) * length * channels bytes allocated to it
    // data[0], data[1]...data[length-1] is channel 0,
    // data[length], data[length+1]...data[2*length-1] is channel 1, 
    // etc
    double * data;


} audio_t;



// useful for most things
#define PARAM_SCALE_LINEAR 0x00

// useful for cutoff frequency (in hz) since log(hz) is semitones, and is what really matters
#define PARAM_SCALE_LOG 0x01

// parameter info
typedef struct _chparam_s {

    double minimum, maximum;

    // see PARAM_SCALE_* macros
    int32_t scale;

    // false if there is no min/max/scale
    int32_t is_applied;

} chparam_t;



#define OBJTYPE_DOUBLE 0x0001
#define OBJTYPE_INT 0x0002
#define OBJTYPE_STRING 0x0003
#define OBJTYPE_AUDIO 0x0004
#define OBJTYPE_ANY 0x0005

// return on error
#define OBJTYPE_NOTFOUND 0x0101


// for storing data in dictionaries
typedef struct _chdictobj_s {

    // OBJTYPE_* macros
    int32_t type;

    union {

        int ival;
        double dval;
        char * sval;
        audio_t aval;
        void * pval;

    } val;

    // only useful if it's a double
    chparam_t param_info;

} chdictobj_t;

typedef struct _chdict_s {
    
    int len;
    char ** keys;
    chdictobj_t * vals;

} chdict_t;



// should return a pointer to some structure type that is used internally for the project.
// should not return NULL (unless a failure has occured)
// dict may be NULL!
// if not, cast to chdict_t *
typedef void * (*chaudio_PluginInit)(int32_t channels, int32_t sample_rate, chdict_t * dict);

// plugin_data is the same pointer created by the ch_PluginInit function
// returns status code (0 = sucess)
// 'in' and 'out' are both of length N * channels,
// they are stored Channel wise, so LLLLLLLRRRRRRRR data for stereo
// there are N samples for each channel
// dictionary may be NULL!
// if not, cast to chdict_t *
typedef int32_t (*chaudio_PluginProcess)(void * plugin_data, double * in, double * out, int32_t N, chdict_t * dict);

// just the de-initializer
typedef int32_t (*chaudio_PluginFree)(void * plugin_data);

// most of the time, other programs will want
typedef struct _chaudio_plugin_s {

    chaudio_PluginInit init;
    chaudio_PluginProcess process;
    chaudio_PluginFree free;

    void * plugin_data;

    uint32_t channels, sample_rate;

    chdict_t * dict;

    // in out variables

    double * in, * out;

} chaudio_plugin_t;

#define CHAUDIO_CREATE_PLUGIN(initfunc, processfunc, freefunc) ((ch_plugin_t){ .init = initfunc, .process = processfunc, .free = freefunc, .plugin_data = NULL, .in = NULL, .out = NULL, .dict = NULL })




#endif




