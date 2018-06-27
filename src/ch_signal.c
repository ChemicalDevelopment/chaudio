
#include "chaudio.h"

#include "ch_signal.h"

#include <math.h>

// basic instrumentation
void chaudio_signal_generate(audio_t * output, int32_t waveform, double hz, double phase_offset) {
    if (output == NULL || output->data == NULL) {
        chaudio_set_error("signal generation encountered uninitialized output");
    }

    int i, j;
    double cur_sample;
    double tmp0;
    for (i = 0; i < output->length; ++i) {
        if (waveform == WAVEFORM_SIN) {
            cur_sample = sin(2 * M_PI * ((hz * i) / output->sample_rate + phase_offset));
        } else if (waveform == WAVEFORM_SQUARE) {
            tmp0 = (hz * i) / output->sample_rate + phase_offset;
            tmp0 = tmp0 - floor(tmp0);
            cur_sample = (double)(2 * (tmp0 > 0.5) - 1);
        }
        for (j = 0; j < output->channels; ++j) {
            output->data[i + j * output->length] = cur_sample;
        }
    }


}


