
#include "chaudio.h"

#include <stdlib.h>
#include <string.h>

// for dynamic loading
#include <dlfcn.h>


chaudio_plugin_t chaudio_plugin_create(char * name, chaudio_PluginInit _init, chaudio_PluginProcess _process, chaudio_PluginFree _free) {
    chaudio_plugin_t plugin;

    plugin.name = malloc(strlen(name) + 1);
    strcpy(plugin.name, name);

    plugin.dict = NULL;

    plugin.plugin_data = NULL;

    plugin.in = NULL;
    plugin.out = NULL;

    plugin.init = _init;
    plugin.process = _process;
    plugin.free = _free;

    return plugin;
}

void chaudio_plugin_init(chaudio_plugin_t * plugin, uint32_t channels, uint32_t sample_rate) {
    plugin->dict = (chdict_t *)malloc(sizeof(chdict_t));

    chdict_init(plugin->dict);

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

chaudio_plugin_t chaudio_plugin_load(char * file_name) {
    void * plugin_handle = dlopen(file_name, RTLD_NOW);
    if (plugin_handle == NULL) {
        printf("error could not open file '%s'\n", file_name);
        return CHAUDIO_PLUGIN_NULL;
    }

    chaudio_plugin_t (*plugin_init_func)(chaudioplugin_init_t) = dlsym(plugin_handle, "chaudioplugin_init");

    char * result = dlerror();
    if (plugin_init_func == NULL || result != NULL) {
        printf("ERROR: couldn't find 'chaudioplugin_init' method for file '%s', (err='%s')\n", file_name, result);
        return CHAUDIO_PLUGIN_NULL;
    }

    chaudioplugin_init_t init_val = (chaudioplugin_init_t) { 
        .chdict_get_double = chdict_get_double,
        .chaudio_plugin_create = chaudio_plugin_create
        
    };

    return plugin_init_func(init_val);

}


