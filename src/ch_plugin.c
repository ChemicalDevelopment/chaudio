
#include "ch_plugin.h"
#include "chaudio.h"
#include "dict.h"

#include <stdlib.h>
#include <string.h>



chaudio_plugin_t chaudio_plugin_create(chaudio_PluginInit _init, chaudio_PluginProcess _process, chaudio_PluginFree _free) {
    chaudio_plugin_t plugin;
    plugin.dict = (chdict_t *)malloc(sizeof(chdict_t));

    chdict_init(plugin.dict);

    plugin.plugin_data = NULL;

    plugin.in = NULL;
    plugin.out = NULL;

    plugin.init = _init;
    plugin.process = _process;
    plugin.free = _free;

    return plugin;
}

void chaudio_plugin_init(chaudio_plugin_t * plugin, uint32_t channels, uint32_t sample_rate) {
    plugin->channels = channels;
    plugin->sample_rate = sample_rate;

    if (plugin->init != NULL) plugin->plugin_data = plugin->init(channels, sample_rate, plugin->dict);

}

// 'to' cannot be NULL
audio_t chaudio_plugin_transform(chaudio_plugin_t * plugin, audio_t from, int32_t bufsize, audio_t * output) {
    // ensure enough space
    audio_t into;
    if (output == NULL) {
        into = chaudio_audio_create(plugin->channels, from.length, from.sample_rate);
    } else {
        into = *output;
        chaudio_audio_realloc(&into, plugin->channels, from.length, from.sample_rate);
    }
    
    plugin->in = (double *)realloc(plugin->in, sizeof(double) * bufsize * plugin->channels);
    plugin->out = (double *)realloc(plugin->out, sizeof(double) * bufsize * plugin->channels);

    int32_t i;
    for (i = 0; i < from.length; i += bufsize) {
        int cur_len = bufsize;

        // if its near the last
        if (from.length - i < bufsize) cur_len = from.length - i;
        int32_t c, j;

        for (c = 0; c < plugin->channels && c < from.channels; ++c) {
            for (j = 0; j < cur_len; ++j) {
                //printf("%d\n", c * cur_len + j);
                plugin->in[c * cur_len + j] = from.data[c * from.length + i + j];
                plugin->out[c * cur_len + j] = (double)0.0;
            }
        }

        // now actually process it
        if (plugin->process != NULL) {
            plugin->process(plugin->plugin_data, plugin->in, plugin->out, cur_len, plugin->dict);
        }
        
        //printf("asdf\n");

        // copy to output
        for (c = 0; c < plugin->channels && c < into.channels; ++c) {
            for (j = 0; j < cur_len; ++j) {
                into.data[c * into.length + i + j] = plugin->out[c * cur_len + j];
            }
        }
    }



    if (output != NULL) *output = into;

    return into;
}

int32_t chaudio_plugin_free(chaudio_plugin_t * plugin) {
    if (plugin->free != NULL) {
        int32_t res = plugin->free(plugin->plugin_data);
        if (res != 0) printf("Warning: plugin being freed had a non-zero code: %d\n", res);
        return res;
    }
    return 0;
}



/* example plugins */


// basic storage type
typedef struct _gain_data_s {
    int32_t channels;
    int32_t sample_rate;
} gain_data_t;


chaudio_PluginInit chaudio_gain_init(int32_t channels, int32_t sample_rate, chdict_t * dict) {
    chdict_t * chdict = (chdict_t *)dict;

    // now, register parameters (default, min, max, scale type)
    chdict_set(chdict, "gain", chdictobj_double_info(0.0, -40.0, 40.0, PARAM_SCALE_LINEAR));

    gain_data_t * this_data = (gain_data_t *)malloc(sizeof(gain_data_t));

    this_data->sample_rate = sample_rate;
    this_data->channels = channels;

    // return it as a void pointer
    return (void *)this_data;
}

chaudio_PluginProcess chaudio_gain_process(void * plugin_data, double * in, double * out, int32_t N, chdict_t * dict) {

    // theoretically should NULL check here
    chdict_t * chdict = (chdict_t *)dict;
    gain_data_t this_data = *(gain_data_t *)plugin_data;

    chdictobj_t gain_obj = chdict_get(chdict, "gain");

    double gain_db = 0.0;
    if (gain_obj.type == OBJTYPE_DOUBLE) {
        gain_db = gain_obj.val.dval;
    }

    double gain_coef = pow(10.0, gain_db / 20.0);

    int c, i;
    for (c = 0; c < this_data.channels; ++c) {
        for (i = 0; i < N; ++i) {
            out[c * N + i] = gain_coef * in[c * N + i];
        }
    }

    return 0;
}


chaudio_PluginFree chaudio_gain_free(void * plugin_data) {
    if (plugin_data != NULL) free(plugin_data);
}

chaudio_plugin_t chaudio_plugin_gain;

void chaudio_plugin_create_defaults() {
  chaudio_plugin_gain = chaudio_plugin_create(chaudio_gain_init, chaudio_gain_process, chaudio_gain_free);
}


