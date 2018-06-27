

#include "chaudio.h"
#include "util.h"

#include <stdlib.h>

#include <math.h>



double double_limit(double x, double min_val, double max_val) {
    if (x <= min_val) {
        return min_val;
    } else if (x >= max_val) {
        return max_val;
    } else {
        return x;
    }
}


double chaudio_get_seconds(audio_t audio) {
    return (double)audio.length / audio.sample_rate;
}


audio_t * chaudio_copy(audio_t * output, audio_t input) {
    // dont need to copy to itself
    if (output != NULL && output->data == input.data) return output;

    if (output == NULL) {
        // if its nothing, or its being called on itself
        output = (audio_t *)malloc(sizeof(audio_t));
        chaudio_create_audio_from_audio(output, input);
        return output;
    } else {
        chaudio_realloc(output, input.channels, input.length);
        output->sample_rate = input.sample_rate;
        int i;
        for (i = 0; i < input.length * input.channels; ++i) {
            output->data[i] = input.data[i];
        }
        return output;
    }
}

// give it NULL as output to automatically return a correctly allocated array.
// You must free it if so
// if output is the same as input, it is freed and a new values is returned
audio_t * chaudio_resample(audio_t * output, audio_t input, int new_sample_rate) {
    int new_length = (int)floor(((double)new_sample_rate * input.length) / input.sample_rate + 0.5);

    bool are_same = (output != NULL) && (input.data == output->data);

    if (output == NULL || are_same) {
        output = (audio_t *)malloc(sizeof(audio_t));
        
        if (chaudio_create_audio(output, input.channels, new_length, new_sample_rate) < 0) {
            return NULL;
        }
    } else {
        if (chaudio_realloc(output, input.channels, new_length) < 0) {
            return NULL;
        }
    }
    output->length = new_length;
    output->sample_rate = new_sample_rate;

    if (input.sample_rate % new_sample_rate == 0) {
        // perfect slicing
        int ratio = input.sample_rate / new_sample_rate;
        int i, j;
        for (i = 0; i < output->length; ++i) {
            for (j = 0; j < output->channels; ++j) {
                output->data[i + j * output->length] = input.data[ratio * i + j * input.length];
            }
        }

    } else {
        // interpolation
        double ratio = (double)input.sample_rate / new_sample_rate;
        int i, j;
        double wanted_sample;

        double s0, s1, prop;

#define LIN_MIX(a, b, p) ((a) * (1.0 - p) + (b) * (p))

        for (i = 0; i < new_length; ++i) {
            wanted_sample = ratio * i;
            for (j = 0; j < output->channels; ++j) {
                s0 = input.data[(int)floor(wanted_sample) + j * input.length];
                if ((int)floor(wanted_sample) >= input.length - 1) {
                    s1 = 0.0;
                } else {
                    s1 = input.data[(int)floor(wanted_sample) + 1 + j * input.length];
                }
                prop = wanted_sample - floor(wanted_sample);
                output->data[i + j * output->length] = LIN_MIX(s0, s1, prop);
            }
        }
    }


    if (are_same) chaudio_destroy_audio(&input);

    return output;

    // resample using standard appraoch
}



audio_t * chaudio_mix_to_mono(audio_t * output, audio_t input) {

    // this is just used for updating the length
    bool are_same = (output != NULL) && (input.data == output->data);

    // we dont need to recreate if it is the same
    if (output == NULL) {
        output = (audio_t *)malloc(sizeof(audio_t));
        chaudio_create_audio(output, 1, input.length, input.sample_rate);
    } else {
        chaudio_realloc(output, 1, input.length);
        output->sample_rate = input.sample_rate;
    }

    double cur_sum = 0.0;

    int i, j;
    for (i = 0; i < input.length; ++i) {
        cur_sum = 0.0;
        for (j = 0; j < input.channels; ++j) {
            cur_sum += input.data[i + j * input.length];
        }
        // normalized value so no clipping from mix
        output->data[i] = cur_sum / input.channels;
    }

    return output;
}


audio_t * chaudio_normalize(audio_t * output, audio_t input) {

    bool output_exists = output != NULL;
    bool are_same = output_exists && (input.data == output->data);

    double abs_input_max;
    double tmp;

    int i;
    for (i = 0; i < input.length * input.channels; ++i) {
        tmp = fabs(input.data[i]);
        if (tmp > abs_input_max) {
            abs_input_max = tmp;
        }
    }
    // blank, should just copy
    if (abs_input_max == 0.0) {
        if (are_same) {
            // do nothing, its normalized
        } else {
            if (output_exists) {
                chaudio_realloc(output, input.channels, input.length);
                output->sample_rate = input.sample_rate;
            } else {
                output = (audio_t *)malloc(sizeof(audio_t));
                chaudio_create_audio(output, input.channels, input.length, input.sample_rate);
            }
        }
    } else if (abs_input_max == 1.0) { // already normalized
        if (are_same) {
            // do nothing, its normalized
        } else {
            if (output_exists) {
                chaudio_copy(output, input);
            } else {
                output = (audio_t *)malloc(sizeof(audio_t));
                chaudio_copy(output, input);
            }
        }
    } else {
        if (output_exists) {
            chaudio_realloc(output, input.channels, input.length);
            output->sample_rate = input.sample_rate;
        } else {
            output = (audio_t *)malloc(sizeof(audio_t));
            chaudio_create_audio(output, input.channels, input.length, input.sample_rate);
        }
        for (i = 0; i < input.length * input.channels; ++i) {
            output->data[i] = input.data[i] / abs_input_max;
        }
    }

    return output;
}

// audio re-voluming
audio_t * chaudio_gain(audio_t * output, audio_t input, double db) {
    bool output_exists = output != NULL;
    bool are_same = output_exists && (input.data == output->data);

    double coef = GAIN_COEF(db);

    if (output_exists) {
        if (are_same) {
            // do nothing
        } else {
            chaudio_realloc(output, input.channels, input.length);
            output->sample_rate = input.sample_rate;
        }
    } else {
        output = (audio_t *)malloc(sizeof(audio_t));
        chaudio_create_audio(output, input.channels, input.length, input.sample_rate);
    }

    int i;
    for (i = 0; i < input.length * input.channels; ++i) {
        output->data[i] = coef * input.data[i];
    }

    return output;
}

// pad to length
audio_t * chaudio_adjust_length(audio_t * output, audio_t input, int to_length) {

    bool are_same = output != NULL && output->data != input.data;
    
    if (output == NULL) {
        output = (audio_t *)malloc(sizeof(audio_t));
        chaudio_create_audio(output, input.channels, to_length, input.sample_rate);
    } else {
        chaudio_realloc(output, input.channels, to_length);
        output->sample_rate = input.sample_rate;
    }


    int i, j;
    for (i = 0; i < output->length; ++i) {
        for (j = 0; j < output->channels; ++j) {
            if (i < input.length && !are_same) {
                output->data[i + j * output->length] = input.data[i + j * input.length];
            } else {
                output->data[i + j * output->length] = 0.0;
            }
        }
    }
}

audio_t * chaudio_pad(audio_t * output, audio_t input, int added_zeros) {
    return chaudio_adjust_length(output, input, input.length + added_zeros);
}


audio_t * chaudio_append(audio_t * output, audio_t input_A, audio_t input_B) {
    int new_length = input_A.length + input_B.length;
    int new_channels = input_A.channels;
    if (input_B.channels > input_A.channels) {
        new_channels = input_B.channels;
    }

    int new_sample_rate = input_A.sample_rate;
    if (input_B.sample_rate > input_A.sample_rate) {
        new_sample_rate = input_B.sample_rate;
    }

    if (output == NULL) {
        output = (audio_t *)malloc(sizeof(audio_t));
        chaudio_create_audio(output, new_channels, new_length, new_sample_rate);
    } else {
        chaudio_realloc(output, new_channels, new_length);
        output->sample_rate = new_sample_rate;
    }

    int i, j;

    int cc = 0;

    for (i = 0; i < new_length; ++i) {
        for (j = 0; j < new_channels; ++j) {
            if (i < input_A.length) {
                if (j < input_A.channels) {
                    cc = j;
                } else {
                    cc = 0;
                }
                output->data[i + j * new_length] = input_A.data[i + cc * input_A.length];
            } else {
                int ci = i - input_B.length;
                if (j < input_B.channels) {
                    cc = j;
                } else {
                    cc = 0;
                }
                output->data[i + j * new_length] = input_B.data[ci + cc * input_B.length];
            }
        }
    }

    return output;
}


