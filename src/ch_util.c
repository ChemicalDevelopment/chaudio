

#include "chaudio.h"
#include "util.h"

#include <stdlib.h>

#include <math.h>



double double_limit(double x, double min_val, double max_val) {
    if (x < min_val) {
        return min_val;
    } else if (x > max_val) {
        return max_val;
    } else {
        return x;
    }
}


audio_t * chaudio_copy(audio_t * output, audio_t input) {
    if (output == NULL) {
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
audio_t * chaudio_resample(audio_t * output, audio_t input, int new_sample_rate) {
    int new_length = (int)floor(((double)new_sample_rate * input.length) / input.sample_rate + 0.5);

    if (output == NULL) {
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

    return output;

    // resample using standard appraoch
}



