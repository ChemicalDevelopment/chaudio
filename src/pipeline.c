
#include "chaudio.h"

chaudio_pipeline_t chaudio_pipeline_create(int32_t channels, int32_t sample_rate) {
    chaudio_pipeline_t res;
    res.plugins_len = 0;
    res.plugins = NULL;

    res.generator = NULL;
    res.output = NULL;

    res.in = NULL;
    res.out = NULL;

    res.channels = channels;
    res.sample_rate = sample_rate;
    return res;
}

// plugin shouldn't be initialized
void chaudio_pipeline_add(chaudio_pipeline_t * pipeline, chaudio_plugin_t plugin) {
    pipeline->plugins_len++;
    pipeline->plugins = realloc(pipeline->plugins, pipeline->plugins_len * sizeof(chaudio_plugin_t));

    chaudio_plugin_t new_plugin = chaudio_plugin_create_plugin(plugin);

    chaudio_plugin_init(&new_plugin, pipeline->channels, pipeline->sample_rate);

    pipeline->plugins[pipeline->plugins_len - 1] = new_plugin;

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


void chaudio_pipeline_init(chaudio_pipeline_t * pipeline) {
    chaudio_generator_init(pipeline->generator, pipeline->channels, pipeline->sample_rate);
    chaudio_output_init(pipeline->output, pipeline->channels, pipeline->sample_rate);
}

void chaudio_pipeline_runstream(chaudio_pipeline_t * pipeline, int32_t bufsize, double audio_length, chaudio_IsFinished stop_func) {

    pipeline->in = realloc(pipeline->in, sizeof(double) * pipeline->channels * bufsize);
    pipeline->out = realloc(pipeline->out, sizeof(double) * pipeline->channels * bufsize);

    // for swapping buffers
    void * _tmp;
    int i;

    int loops = 0;

    bool keep_going = true;

    int32_t gen_res = CHAUDIO_CONTINUE;

    while (keep_going) {
        if (pipeline->generator == NULL) {
            // set to all zeros
            for (i = 0; i < pipeline->channels * bufsize; ++i) pipeline->in[i] = 0.0;
        } else {
            // get our generated values
            gen_res = pipeline->generator->generate(pipeline->generator->generator_data, pipeline->in, bufsize);
        }

        if (gen_res == CHAUDIO_FINISHED) {
            keep_going = false;
        }

        // now process it
        for (i = 0; i < pipeline->plugins_len; ++i) {
            if (i != 0) {
                // swap buffers so it works like a chain
                _tmp = pipeline->in;
                pipeline->in = pipeline->out;
                pipeline->out = _tmp;
            }
            pipeline->plugins[i].process(pipeline->plugins[i].plugin_data, pipeline->in, pipeline->out, bufsize);
        }

        chaudio_output_dump(pipeline->output, pipeline->out, bufsize);

        /* some basic diagnostics, tells peaks
        double mx = 0.0;
        for (i = 0; i < pipeline->channels * bufsize; ++i) {
            if (fabs(out[i]) > mx) mx = fabs(out[i]);
        }

        if (loops % 50 == 0) printf("mx: %lf\n", mx);
        */
       
        loops++;

        if (audio_length > 0 && loops * bufsize > pipeline->sample_rate * audio_length) {
            keep_going = false;
        }

        if (stop_func != NULL && stop_func()) {
            keep_going = false;
        }

    }

}



void chaudio_pipeline_free(chaudio_pipeline_t * pipeline) {
    chaudio_generator_free(pipeline->generator);
    chaudio_output_free(pipeline->output);
    
    int i;

    for (i = 0; i < pipeline->plugins_len; ++i) {
        chaudio_plugin_free(&pipeline->plugins[i]);
    }
}

