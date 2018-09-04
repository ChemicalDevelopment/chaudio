
#include "chaudio.h"

#include <stdlib.h>
#include <string.h>

// for dynamic loading
#include <dlfcn.h>



chaudio_plugin_t chaudio_plugin_create(char * name, chaudio_PluginInit _init, chaudio_PluginProcess _process, chaudio_PluginFree _free, chaudio_paraminterface_t params) {
    chaudio_plugin_t plugin;

    plugin.name = malloc(strlen(name) + 1);
    strcpy(plugin.name, name);

    plugin.plugin_data = NULL;

    plugin.in = NULL;
    plugin.out = NULL;

    plugin.init = _init;
    plugin.process = _process;
    plugin.free = _free;

    plugin.params = params;

    return plugin;
}


chaudio_plugin_t chaudio_plugin_create_plugin(chaudio_plugin_t plg) {
    chaudio_plugin_t r;
    r.name = malloc(strlen(plg.name) + 1);
    strcpy(r.name, plg.name);

    r.init = plg.init;
    r.process = plg.process;
    r.free = plg.free;

    r.params = plg.params;

    // reset some stuff
    r.plugin_data = NULL;
    r.in = NULL;
    r.out = NULL;

    return r;
}

void chaudio_plugin_init(chaudio_plugin_t * plugin, int channels, int sample_rate) {
    plugin->channels = channels;
    plugin->sample_rate = sample_rate;

    if (plugin->init != NULL) plugin->plugin_data = plugin->init(channels, sample_rate);

}

// 'to' cannot be NULL
audio_t chaudio_plugin_transform(chaudio_plugin_t * plugin, audio_t from, int bufsize, audio_t * output) {
    // ensure enough space
    audio_t into;
    if (output == NULL) {
        into = chaudio_audio_create(from.length, plugin->channels, from.sample_rate);
    } else {
        into = *output;
        chaudio_audio_realloc(&into, from.length, plugin->channels, from.sample_rate);
    }

    
    plugin->in = (double *)realloc(plugin->in, sizeof(double) * bufsize * plugin->channels);
    plugin->out = (double *)realloc(plugin->out, sizeof(double) * bufsize * plugin->channels);

    int i;
    for (i = 0; i < from.length; i += bufsize) {
        int cur_len = bufsize;

        // if its near the last
        if (from.length - i < bufsize) cur_len = from.length - i;
        int c, j, k;


        for (j = 0; j < cur_len; ++j) {
            for (k = 0; k < plugin->channels && k < from.channels; ++k) {
                plugin->in[plugin->channels * j + k] = from.data[from.channels * (i + j) + k];
                plugin->out[plugin->channels * j + k] = 0.0;
            }
        }

        // now actually process it
        if (plugin->process != NULL) {
            plugin->process(plugin->plugin_data, plugin->in, plugin->out, cur_len);
        }


        // copy to output
        for (j = 0; j < cur_len; ++j) {
            for (k = 0; k < into.channels && k < from.channels; ++k) {
                into.data[into.channels * (i + j) + k] = plugin->out[plugin->channels * j + k];

            }
        }
        
    }

    if (output != NULL) *output = into;

    return into;
}

int chaudio_plugin_free(chaudio_plugin_t * plugin) {
    if (plugin->free != NULL) {
        int res = plugin->free(plugin->plugin_data);
        if (res != 0) printf("Warning: plugin being freed had a non-zero code: %d\n", res);
        return res;
    }
    return 0;
}



/* example plugins */


chaudio_plugin_t _plugin_load(char * file_name) {
    void * plugin_handle = dlopen(file_name, RTLD_NOW);

    if (plugin_handle == NULL) {
        // printf("chaudio: could not open plugin '%s': %s\n", file_name, dlerror());
        return (chaudio_plugin_t) { .name = NULL };
    }

    chaudio_plugin_t (*export_init_func)(chaudio_dl_init_t) = dlsym(plugin_handle, "chaudioplugin_export");

    char * result = dlerror();
    if (export_init_func == NULL || result != NULL) {
        //printf("chaudio: could not find plugin export (err='%s'), '%s' may be a generator or output\n", result, file_name);
        return (chaudio_plugin_t) { .name = NULL };
    }

    return export_init_func(chaudio_dl_init());
}

chaudio_plugin_t chaudio_plugin_load(char * file_name) {


    chaudio_plugin_t r = _plugin_load(file_name);

    if (CHAUDIO_PLUGIN_ISVALID(r)) {
        return r;
    } else if (getenv("CHAUDIO_PATH") != NULL) {
        char * chaudio_path = malloc(strlen(getenv("CHAUDIO_PATH")) + 1);
        strcpy(chaudio_path, getenv("CHAUDIO_PATH"));
        char * cur_check = malloc(strlen(chaudio_path) + strlen(file_name) + 4096 + 1);

        int i;
        char * cur_dir = strtok(chaudio_path, ":");
        
        while (cur_dir != NULL) {
            // different library naming conventions
            #ifdef __linux__
            sprintf(cur_check, "%s/plugins/lib%s.so", cur_dir, file_name);
            #endif

            #ifdef __APPLE__
            sprintf(cur_check, "%s/plugins/lib%s.dylib", cur_dir, file_name);
            #endif
            
            /*

            TODO: consider windows formatting for libraries

            */
            #ifdef _WINDOWS
            sprintf(cur_check, "%s/plugins/%s.dll", cur_dir, file_name);
            #endif

            // printf("checking file: '%s'\n" ,cur_check);
            r = _plugin_load(cur_check);

            if (CHAUDIO_PLUGIN_ISVALID(r)) {
                break;
            }

            cur_dir = strtok(NULL, ":");
        }
        free(cur_check);
        free(chaudio_path);
        if (CHAUDIO_PLUGIN_ISVALID(r)) return r;
    }

    return (chaudio_plugin_t) { .name = NULL };
}


