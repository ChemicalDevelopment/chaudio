/*

basic signal synthesis

*/


#ifndef __CH_SIGNAL_H__
#define __CH_SIGNAL_H__


#define WAVEFORM_SIN  0x0001
#define WAVEFORM_SQUARE  0x0002


#define PHASE_DEGREES(n) ((n) / 360.0)
#define PHASE_RADIANS(n) ((n) / (2 * M_PI));

#include "chaudio.h"

// basic instrumentation
// `output` should be initialized, this fills the buffer with signal
// phase_offset is in [0,1] in cycle
// so, 180 degrees is 0.5

void chaudio_signal_generate(audio_t * output, int32_t waveform, double hz, double phase_offset);


#endif

