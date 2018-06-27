
#include "ch_plugin.h"
#include <stdlib.h>
#include <string.h>

plugin_param_t chaudio_param_create_int(int val) {
    plugin_param_t ret;
    ret.type = PARAM_TYPE_INT;
    ret._int_val = val;
    ret._double_val = (double)val;
    ret._audio_val = NULL;
    ret.val = NULL;
}

plugin_param_t chaudio_param_create_double(double val) {
    plugin_param_t ret;
    ret.type = PARAM_TYPE_DOUBLE;
    ret._int_val = (double)floor(val + 0.5);
    ret._double_val = val;
    ret._audio_val = NULL;
    ret.val = NULL;
}


plugin_param_t chaudio_param_create_string(char * val) {
    plugin_param_t ret;
    ret.type = PARAM_TYPE_STRING;
    ret._int_val = 0;
    ret._double_val = 0.0;
    ret._audio_val = NULL;
    ret.val = strdup(val);
}

plugin_param_t chaudio_param_create_audio(audio_t * val) {
    plugin_param_t ret;
    ret.type = PARAM_TYPE_AUDIO;
    ret._int_val = 0;
    ret._double_val = 0.0;
    ret.val = NULL;

    ret._audio_val = (audio_t *)malloc(sizeof(audio_t));

    chaudio_create_audio_from_audio(ret._audio_val, *val);
}

plugin_param_t chaudio_param_create_audio_reference(audio_t * val) {
    plugin_param_t ret;
    ret.type = PARAM_TYPE_AUDIO;
    ret._int_val = 0;
    ret._double_val = 0.0;
    ret._audio_val = val;
    ret.val = NULL;
}


plugin_param_t chaudio_param_create_any(void * val, int Nbytes) {
    plugin_param_t ret;
    ret.type = PARAM_TYPE_ANY;
    ret._int_val = 0;
    ret._double_val = 0.0;
    ret._audio_val = NULL;
    ret.val = (void *)malloc(Nbytes);
    memcpy(ret.val, val, Nbytes);
}

void chaudio_param_free(plugin_param_t * param) {
    if ((param->type == PARAM_TYPE_ANY || param->type == PARAM_TYPE_STRING) && (param->val != NULL)) {
        free(param->val);
        param->val = NULL;
    }
    if (param->type == PARAM_TYPE_AUDIO) {
        chaudio_destroy_audio(param->_audio_val);
        free(param->_audio_val);
        param->_audio_val = NULL;
    }
}



void chaudio_plugin_init(audio_plugin_t * plugin, audio_plugin_func_t plugin_func, uint16_t channels, uint32_t length, uint32_t sample_rate) {
    plugin->num_params = 0;
    plugin->param_keys = NULL;
    plugin->param_vals = NULL;

    plugin->plugin_func = plugin_func;

    chaudio_create_audio(&plugin->in, channels, length, sample_rate);
    chaudio_create_audio(&plugin->out, channels, length, sample_rate);
}

void chaudio_plugin_free(audio_plugin_t * plugin) {

    int i;
    for (i = 0; i < plugin->num_params; ++i) {
        free(plugin->param_keys[i]);
        chaudio_param_free(&plugin->param_vals[i]);
    }

    free(plugin->param_keys);
    free(plugin->param_vals);

    chaudio_destroy_audio(&plugin->in);
    chaudio_destroy_audio(&plugin->out);

    plugin->num_params = 0;

    plugin->param_keys = NULL;
    plugin->param_vals = NULL;

}

void chaudio_plugin_set_func(audio_plugin_t * plugin, audio_plugin_func_t * func) {
    plugin->plugin_func = func;
}


int chaudio_plugin_param_add(audio_plugin_t * plugin, char * key, plugin_param_t param) {
    plugin->num_params += 1;
    plugin->param_keys = (char *)realloc((void *)plugin->param_keys, sizeof(char *) * plugin->num_params);

    plugin->param_vals = (char *)realloc((void *)plugin->param_vals, sizeof(plugin_param_t) * plugin->num_params);

    int res_i = plugin->num_params - 1;

    plugin->param_keys[res_i] = strdup(key);
    plugin->param_vals[res_i].type = param.type;
    plugin->param_vals[res_i].val = param.val;
    plugin->param_vals[res_i]._int_val = param._int_val;
    plugin->param_vals[res_i]._double_val = param._double_val;
    plugin->param_vals[res_i]._audio_val = param._audio_val;

    return res_i;
}

int _plugin_get_idx(audio_plugin_t * plugin, char * key) {
    int i;
    for (i = 0; i < plugin->num_params; ++i) {
        if (strcmp(plugin->param_keys[i], key) == 0) {
            return i;
        }
    }
    return -1;
}

void chaudio_plugin_param_set_int(audio_plugin_t * plugin, char * key, int val) {
    int idx = _plugin_get_idx(plugin, key);
    if (idx < 0) {
        idx = chaudio_plugin_param_add(plugin, key, chaudio_param_create_int(val));
    }
    plugin->param_vals[idx]._int_val = val;
}


void chaudio_plugin_param_set_double(audio_plugin_t * plugin, char * key, double val) {
    int idx = _plugin_get_idx(plugin, key);
    if (idx < 0) {
        idx = chaudio_plugin_param_add(plugin, key, chaudio_param_create_double(val));
    }
    plugin->param_vals[idx]._double_val = val;
}


void chaudio_plugin_param_set_string(audio_plugin_t * plugin, char * key, char * val) {
    int idx = _plugin_get_idx(plugin, key);
    if (idx < 0) {
        idx = chaudio_plugin_param_add(plugin, key, chaudio_param_create_string(val));
    }
    free(plugin->param_vals[idx].val);
    plugin->param_vals[idx].val = (void *)strdup(val);
}


void chaudio_plugin_param_set_audio(audio_plugin_t * plugin, char * key, audio_t * val) {
    int idx = _plugin_get_idx(plugin, key);
    if (idx < 0) {
        idx = chaudio_plugin_param_add(plugin, key, chaudio_param_create_audio(val));
    }
    chaudio_copy(plugin->param_vals[idx]._audio_val, *val);
}



void chaudio_plugin_param_set_audio_reference(audio_plugin_t * plugin, char * key, audio_t * val) {
    int idx = _plugin_get_idx(plugin, key);
    if (idx < 0) {
        idx = chaudio_plugin_param_add(plugin, key, chaudio_param_create_audio_reference(val));
    }
    plugin->param_vals[idx]._audio_val = val;
}



void chaudio_plugin_param_set_any(audio_plugin_t * plugin, char * key, void * val, int Nbytes) {
    int idx = _plugin_get_idx(plugin, key);
    if (idx < 0) {
        idx = chaudio_plugin_param_add(plugin, key, chaudio_param_create_any(val, Nbytes));
    }
    free(plugin->param_vals[idx].val);
    plugin->param_vals[idx].val = malloc(Nbytes);
    memcpy(plugin->param_vals[idx].val, val, Nbytes);
}

int chaudio_plugin_param_get_int(audio_plugin_t * plugin, char * key) {
    int idx = _plugin_get_idx(plugin, key);
    if (idx >= 0) {
        return plugin->param_vals[idx]._int_val;
    } else {
        return 0;
    }
}


double chaudio_plugin_param_get_double(audio_plugin_t * plugin, char * key) {
    int idx = _plugin_get_idx(plugin, key);
    if (idx >= 0) {
        return plugin->param_vals[idx]._double_val;
    } else {
        return 0.0;
    }
}


char * chaudio_plugin_param_get_string(audio_plugin_t * plugin, char * key) {
    int idx = _plugin_get_idx(plugin, key);
    if (idx >= 0) {
        return (char *)plugin->param_vals[idx].val;
    } else {
        chaudio_set_error("invalid parameter key");
        return NULL;
    }
}

audio_t * chaudio_plugin_param_get_audio(audio_plugin_t * plugin, char * key) {
    int idx = _plugin_get_idx(plugin, key);
    if (idx >= 0) {
        return chaudio_copy(NULL, *plugin->param_vals[idx]._audio_val);
    } else {
        chaudio_set_error("invalid parameter key");
        return NULL;
    }
}

// dont free this!
audio_t * chaudio_plugin_param_get_audio_reference(audio_plugin_t * plugin, char * key) {
    int idx = _plugin_get_idx(plugin, key);
    if (idx >= 0) {
        return plugin->param_vals[idx]._audio_val;
    } else {
        chaudio_set_error("invalid parameter key");
        return NULL;
    }
}


void * chaudio_plugin_param_get_any(audio_plugin_t * plugin, char * key) {
    int idx = _plugin_get_idx(plugin, key);
    if (idx >= 0) {
        return plugin->param_vals[idx].val;
    } else {
        chaudio_set_error("invalid parameter key");
        return NULL;
    }
}




audio_t * chaudio_plugin_process_full(audio_plugin_t * plugin, audio_t * output, audio_t input) {
    chaudio_copy(&plugin->in, input);

    chaudio_realloc(&plugin->out, input.channels, input.length);
    plugin->out.sample_rate = input.sample_rate;


    if (plugin->plugin_func == NULL) {
        // just copy
        chaudio_copy(&plugin->out, plugin->in);
    } else {
        plugin->plugin_func(plugin);
    }

    return chaudio_copy(output, plugin->out);
}

audio_t * chaudio_plugin_process_chunks(audio_plugin_t * plugin, audio_t * output, audio_t input, uint32_t chunk_size) {
    audio_t small_chunk_in, small_chunk_out;
    chaudio_create_audio(&small_chunk_in, input.channels, chunk_size, input.sample_rate);
    chaudio_create_audio(&small_chunk_out, input.channels, chunk_size, input.sample_rate);

    if (output == NULL) {
        output = (audio_t *)malloc(sizeof(audio_t));
        chaudio_create_audio(output, input.channels, input.length, input.sample_rate);
    } else {
        chaudio_realloc(output, input.channels, input.length);
        output->sample_rate = input.sample_rate;
    }    


    int i, j, k;
    for (i = 0; i < input.length; i += chunk_size) {
        int cur_chunk_size = input.length - i;
        if (cur_chunk_size > chunk_size) {
            cur_chunk_size = chunk_size;
        }
        chaudio_realloc(&small_chunk_in, small_chunk_in.channels, cur_chunk_size);
        chaudio_realloc(&small_chunk_out, small_chunk_in.channels, cur_chunk_size);

        for (j = 0; j < cur_chunk_size; ++j) {
            for (k = 0; k < small_chunk_in.channels; ++k) {
                small_chunk_in.data[j + k * small_chunk_in.length] = input.data[i + j + k * input.length];
            }
        }

        chaudio_plugin_process_full(plugin, &small_chunk_out, small_chunk_in);

        // copy to current output
        for (j = 0; j < cur_chunk_size; ++j) {
            for (k = 0; k < small_chunk_out.channels; ++k) {
                output->data[i + j + k * output->length] = small_chunk_out.data[j + k * small_chunk_out.length];
            }
        }

    }

    return output;
}


/*

example plugins

*/


// "gain" : controls the gain of the plugin (vol)
audio_plugin_func_t chaudio_plugin_GAIN(audio_plugin_t * plugin) {
    double cur_gain = chaudio_plugin_param_get_double(plugin, "gain");
    chaudio_gain(&plugin->out, plugin->in, cur_gain);
}

// "delay" : controls the length (in seconds) that the plugin delays for. Max 5.0
// "feedback" : how much is written back out: Typically 0, but max of 1 unless extra feedback is wanted
// this creates the effect of more echos each being quieter (0<feedback<1.0), infinitely the same (feedback==1), or growing louder (feedback>1). Negative values just alternate polarity
audio_plugin_func_t chaudio_plugin_DELAY(audio_plugin_t * plugin) {

    int cur_write_idx = chaudio_plugin_param_get_int(plugin, "__cur_write_idx");
    double cur_delay = chaudio_plugin_param_get_double(plugin, "delay");
    double cur_feedback = chaudio_plugin_param_get_double(plugin, "feedback");

    audio_t * big_buffer = NULL;


    if (cur_write_idx == 0) {
        // first time around
        big_buffer = (audio_t *)malloc(sizeof(audio_t));
        chaudio_create_audio(big_buffer, plugin->in.channels, plugin->in.sample_rate * 5, plugin->in.sample_rate);

        chaudio_plugin_param_set_audio_reference(plugin, "__big_buffer", big_buffer);


    } else {
        big_buffer = chaudio_plugin_param_get_audio_reference(plugin, "__big_buffer");
    }


    chaudio_realloc(big_buffer, plugin->in.channels, plugin->in.sample_rate * 5);
    big_buffer->sample_rate = plugin->in.sample_rate;

    int delay_samples = (int)floor(cur_delay * plugin->in.sample_rate + 0.5);

    int i, j;
    for (i = 0; i < plugin->out.length; ++i) {
        if (i - delay_samples >= 0 && i - delay_samples < plugin->in.length) {// in memory from input
            for (j = 0; j < plugin->out.channels; ++j) {
                plugin->out.data[i + j * plugin->out.length] = plugin->in.data[i - delay_samples + j * plugin->in.length];
            }
        } else { // lookup previous values
            int cur_big_buffer = cur_write_idx + i - delay_samples;
            cur_big_buffer = ((cur_big_buffer % big_buffer->length) + big_buffer->length) % big_buffer->length;
            for (j = 0; j < plugin->out.channels; ++j) {
                plugin->out.data[i + j * plugin->out.length] = big_buffer->data[cur_big_buffer + j * big_buffer->length];
            }
        }
    }


    for (i = 0; i < plugin->in.length; ++i) {
        int cur_big_buffer = cur_write_idx + i;
        cur_big_buffer = ((cur_big_buffer % big_buffer->length) + big_buffer->length) % big_buffer->length; 
        for (j = 0; j < plugin->in.channels; ++j) {
            big_buffer->data[cur_big_buffer + j * big_buffer->length] = plugin->in.data[i + j * plugin->in.length] + (cur_feedback * plugin->out.data[i + j * plugin->out.length]);
        }
    }

    // update variables
    chaudio_plugin_param_set_int(plugin, "__cur_write_idx", cur_write_idx + plugin->in.length);

    // done
}


