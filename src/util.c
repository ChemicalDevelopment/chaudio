

#include "chaudio.h"

#include <stdlib.h>

#include <math.h>



double chaudio_audio_duration(audio_t audio) {
    return (double)audio.length / audio.sample_rate;
}


audio_t chaudio_copy(audio_t input, audio_t * output) {
    // dont need to copy to itself
    if (output == NULL) {
        return chaudio_audio_create_audio(input);
    } else {
        chaudio_audio_realloc_audio(output, input);
        int i;
        for (i = 0; i < input.length * input.channels; ++i) {
            output->data[i] = input.data[i];
        }
        return *output;
    }
}

// give it NULL as output to automatically return a correctly allocated array.
// You must free it if so
// if output is the same as input, it is freed and a new values is returned
audio_t chaudio_resample(audio_t input, int64_t new_sample_rate, audio_t * output) {
    int64_t new_length = (int)floor(((double)new_sample_rate * input.length) / input.sample_rate + 0.5);

    audio_t res;

    if (output == NULL) {
        res = chaudio_audio_create(new_length, input.channels, new_sample_rate);
    } else {
        res = *output;
        chaudio_audio_realloc(&res, new_length, input.channels, new_sample_rate);
    }

    if (input.sample_rate % new_sample_rate == 0) {
        // perfect slicing
        int ratio = input.sample_rate / new_sample_rate;
        int i, j;
        for (i = 0; i < res.channels; ++i) {
            for (j = 0; j < res.length; ++j) {
                res.data[i * res.length + j] = input.data[i * input.length + j * ratio];
            }
        }

    } else {
        // TODO: consider other resampling methods
        // interpolation
        double ratio = (double)input.sample_rate / new_sample_rate;
        int i, j;
        double wanted_sample;

        double s0, s1, prop;

#define LIN_MIX(a, b, p) ((a) * (1.0 - p) + (b) * (p))

        for (i = 0; i < res.channels; ++i) {
            for (j = 0; j < new_length; ++j) {
                wanted_sample = ratio * j;
                s0 = input.data[i * input.length + (int)floor(wanted_sample)];
                if ((int)floor(wanted_sample) >= input.length - 1) {
                    s1 = 0.0;
                } else {
                    s1 = input.data[i * input.length + (int)floor(wanted_sample) + 1];
                }
                prop = wanted_sample - floor(wanted_sample);
                res.data[i * res.length + j] = LIN_MIX(s0, s1, prop);
            }
        }
    }

    if (output != NULL) *output = res;

    return res;
}



audio_t chaudio_mix_to_mono(audio_t input, audio_t * output) {

    audio_t res;

    // we dont need to recreate if it is the same
    if (output == NULL) {
        res = chaudio_audio_create(input.length, 1, input.sample_rate);
    } else {
        chaudio_audio_realloc(output, input.length, 1, input.sample_rate);
    }

    double cur_sum = 0.0;

    int i, j;
    for (i = 0; i < input.length; ++i) {
        cur_sum = 0.0;
        for (j = 0; j < input.channels; ++j) {
            cur_sum += input.data[i + j * input.length];
        }
        // normalized value so no clipping from mix
        res.data[i] = cur_sum / input.channels;
    }

    if (output != NULL) *output = res;
    return res;
}


audio_t chaudio_normalize(audio_t input, audio_t * output) {
    
    audio_t res;

    if (output == NULL) {
        res = chaudio_audio_create_audio(input);
    } else {
        res = *output;
        chaudio_audio_realloc_audio(&res, input);
    }

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
        for (i = 0; i < res.length * res.channels; ++i) {
            res.data[i] = 0.0;
        }
    } else {
        for (i = 0; i < res.length * res.channels; ++i) {
            res.data[i] = input.data[i] / abs_input_max;
        }
    }

    if (output != NULL) *output = res;

    return res;
}

// audio re-voluming
audio_t chaudio_gain(audio_t input, double db, audio_t * output) {
    audio_t res;

    if (output == NULL) {
        res = chaudio_audio_create_audio(input);
    } else {
        res = *output;
        chaudio_audio_realloc_audio(&res, input);
    }

    double coef = GAIN_COEF(db);

    int i;
    for (i = 0; i < input.length * input.channels; ++i) {
        res.data[i] = coef * input.data[i];
    }

    if (output != NULL) *output = res;

    return res;
}

audio_t chaudio_pad(audio_t input, int64_t added_zeros, audio_t * output) {
    if (output == NULL) {
        chaudio_copy(input, output);
        chaudio_audio_realloc(output, input.length + added_zeros, 0, 0);
    } else {
        audio_t res = chaudio_audio_create_audio(input);
        chaudio_audio_realloc(&res, input.length + added_zeros, 0, 0);
        return res;
    }
}


/*

appends (or concatenates) audio to another one.

The new length is their sum. 


NOTE: The audio is NOT resampled, and the larger sample rate of the two is taken, and the other is simply treated as being that sample rate. Use `chaudio_resample` before you call this function 

*/
audio_t chaudio_append(audio_t input_A, audio_t input_B, audio_t * output) {
    //
    int64_t new_length = input_A.length + input_B.length;
    int32_t new_channels = input_A.channels;
    if (input_B.channels > input_A.channels) {
        new_channels = input_B.channels;
    }

    int32_t new_sample_rate = input_A.sample_rate;
    if (input_B.sample_rate > input_A.sample_rate) {
        new_sample_rate = input_B.sample_rate;
    }

    audio_t res;

    if (output == NULL) {
        res = chaudio_audio_create(new_length, new_channels, new_sample_rate);
    } else {
        res = *output;
        chaudio_audio_realloc(&res, new_length, new_channels, new_sample_rate);
    }

    int i, j;

    int cc = 0;

    for (i = 0; i < res.channels; ++i) {
        for (j = 0; j < res.length; ++j) {
            if (j < input_A.length) {
                if (i < input_A.channels) {
                    cc = i;
                } else {
                    cc = 0;
                }
                res.data[i * res.length + j] = input_A.data[cc * input_A.length + j];
            } else {
                int cj = j - input_B.length;
                if (i < input_B.channels) {
                    cc = i;
                } else {
                    cc = 0;
                }
                res.data[i * res.length + j] = input_B.data[cc * input_B.length + cj];
            }
        }
    }

    if (output != NULL) *output = res;
    return res;
}


