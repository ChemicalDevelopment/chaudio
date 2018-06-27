/*

basic plugin interface

*/

#ifndef __CH_PLUGIN_H__
#define __CH_PLUGIN_H__

#include "chaudio.h"


// audio plugin

#define PARAM_TYPE_DOUBLE 0x0001
#define PARAM_TYPE_INT 0x0002
#define PARAM_TYPE_STRING 0x0003
#define PARAM_TYPE_AUDIO 0x0004
#define PARAM_TYPE_ANY 0x0005


typedef struct plugin_param_t {

    // can be used as any sort
    void * val;

    // used for more efficient storage of them
    double _double_val;
    int _int_val;

    // storage of an audio chunk
    audio_t * _audio_val;

    // PARAM_TYPE_* macros
    int32_t type;

} plugin_param_t;




typedef struct audio_plugin_t {

    // basic input/output stuff
    audio_t in, out;

    void (*plugin_func)(struct audio_plugin_t *);

    // parameters dictionary structure
    int num_params;
    char ** param_keys;
    plugin_param_t * param_vals;

} audio_plugin_t;

typedef void (*audio_plugin_func_t)(audio_plugin_t * plugin);



plugin_param_t chaudio_param_create_int(int val);
plugin_param_t chaudio_param_create_double(double val);
plugin_param_t chaudio_param_create_string(char * val);
plugin_param_t chaudio_param_create_audio(audio_t * val);
plugin_param_t chaudio_param_create_audio_reference(audio_t * val);
plugin_param_t chaudio_param_create_any(void * val, int Nbytes);


void chaudio_param_free(plugin_param_t * param);

// plugin management

void chaudio_plugin_init(audio_plugin_t * plugin, audio_plugin_func_t func, uint16_t channels, uint32_t length, uint32_t sample_rate);


void chaudio_plugin_free(audio_plugin_t * plugin);

void chaudio_plugin_set_func(audio_plugin_t * plugin, audio_plugin_func_t * func);



int chaudio_plugin_param_add(audio_plugin_t * plugin, char * key, plugin_param_t param);

void chaudio_plugin_param_set_int(audio_plugin_t * plugin, char * key, int val);
void chaudio_plugin_param_set_double(audio_plugin_t * plugin, char * key, double val);
void chaudio_plugin_param_set_string(audio_plugin_t * plugin, char * key, char * val);
void chaudio_plugin_param_set_audio(audio_plugin_t * plugin, char * key, audio_t * val);
void chaudio_plugin_param_set_audio_reference(audio_plugin_t * plugin, char * key, audio_t * val);
void chaudio_plugin_param_set_any(audio_plugin_t * plugin, char * key, void * val, int Nbytes);

int chaudio_plugin_param_get_int(audio_plugin_t * plugin, char * key);
double chaudio_plugin_param_get_double(audio_plugin_t * plugin, char * key);
char * chaudio_plugin_param_get_string(audio_plugin_t * plugin, char * key);
audio_t * chaudio_plugin_param_get_audio(audio_plugin_t * plugin, char * key);
// dont free this!
audio_t * chaudio_plugin_param_get_audio_reference(audio_plugin_t * plugin, char * key);

void * chaudio_plugin_param_get_any(audio_plugin_t * plugin, char * key);


#define chaudio_plugin_process(p, o, i) chaudio_plugin_process_chunks(p, o, i, CHAUDIO_DEFAULT_BUFFER_SIZE)

// for a stream, this can be called multiple times with different sizes of 'input' each time
audio_t * chaudio_plugin_process_full(audio_plugin_t * plugin, audio_t * output, audio_t input);

// the same as above but chunks it up into smaller bits
audio_t * chaudio_plugin_process_chunks(audio_plugin_t * plugin, audio_t * output, audio_t input, uint32_t chunk_size);


/* plugin examples */


audio_plugin_func_t chaudio_plugin_GAIN(audio_plugin_t * plugin);

audio_plugin_func_t chaudio_plugin_DELAY(audio_plugin_t * plugin);



#endif
