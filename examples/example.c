
#include "chaudio.h"

#include <stdlib.h>

int main(int argc, char ** argv) {

    audio_t audio;

    chaudio_create_audio_from_wav_file(&audio, "../data/sin_110.wav");

    // resample it to something lower, just to check it out
    audio_t * result = chaudio_resample(NULL, audio, audio.sample_rate / 2);

    /* manually set these to get cool effects

    result->sample_rate *= 3;
    result->sample_rate /= 2;

    */
    
    chaudio_to_wav_file("./OUTPUT.wav", *result, CHAUDIO_WAVFMT_16I);

    chaudio_destroy_audio(&audio);

    return 0;
}



