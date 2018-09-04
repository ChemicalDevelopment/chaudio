
#include "chaudio.h"


#include <math.h>
#include <stdlib.h>

// basic instrumentation
void chaudio_signal_generate(audio_t * output, int waveform, double hz, double phase_offset) {
    if (output == NULL || output->data == NULL) {
        printf("warning: signal generation encountered uninitialized output\n");
        return;
    }

    int i, j;
    double cur_sample;
    double tmp0;
    for (i = 0; i < output->length; ++i) {
        cur_sample = 0.0;
        if (waveform == CHAUDIO_WAVEFORM_SIN) {
            cur_sample = sin(2 * M_PI * ((hz * i) / output->sample_rate + phase_offset));
        } else if (waveform == CHAUDIO_WAVEFORM_SQUARE) {
            tmp0 = (hz * i) / output->sample_rate + phase_offset;
            tmp0 = tmp0 - floor(tmp0);
            cur_sample = (double)(2 * (tmp0 > 0.5) - 1);
        } else if (waveform == CHAUDIO_WAVEFORM_NOISE) {
            cur_sample = 2.0 * (double)rand() / (RAND_MAX) - 1.0;
        }
        for (j = 0; j < output->channels; ++j) {
            output->data[output->channels * i + j] = cur_sample;
        }
    }


}


