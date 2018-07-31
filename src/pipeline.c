
#include "chaudio.h"

chaudio_pipeline_t chaudio_pipeline_create() {
    chaudio_pipeline_t res;
    res.plugins_len = 0;
    res.plugins = NULL;
    return res;
}

void chaudio_pipeline_add(chaudio_pipeline_t * pipeline, chaudio_plugin_t plugin) {
    pipeline->plugins_len++;
    pipeline->plugins = realloc(pipeline->plugins, pipeline->plugins_len * sizeof(chaudio_plugin_t));
    pipeline->plugins[pipeline->plugins_len - 1] = plugin;

}

audio_t chaudio_pipeline_transform(chaudio_pipeline_t * pipeline, audio_t from, int32_t bufsize, audio_t * output) {
    audio_t res;
    if (output == NULL) {
        res = chaudio_audio_create_audio(from);
    } else {
        res = *output;
    }

    // start off with what we have
    chaudio_copy(from, &res);

    int i;
    for (i = 0; i < pipeline->plugins_len; ++i) {
        // basically overwriting each time
        chaudio_plugin_transform(&pipeline->plugins[i], res, bufsize, &res);
    }

    if (output != NULL) *output = res;
    return res;
}

void chaudio_pipeline_runforever(chaudio_pipeline_t * pipeline, int32_t bufsize) {

    audio_t blank = chaudio_audio_create(bufsize, pipeline->plugins[0].channels, pipeline->plugins[0].sample_rate);
    
    double * in = malloc(bufsize * sizeof(double) * 1), * out = malloc(bufsize * sizeof(double) * 1);

    double *tmp;

    while (1) {
        int i;
        for (i = 0; i < bufsize; ++i) in[i] = 0.0;

        for (i = 0; i < pipeline->plugins_len; ++i) {
            printf("%s\n", pipeline->plugins[i].name);
            pipeline->plugins[i].process(pipeline->plugins[i].plugin_data, in, out, bufsize);
            // swap bois
            tmp = in;
            in = out;
            out = tmp;
        }
    }

}


