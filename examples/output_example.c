
#include "chaudio.h"

#include <stdlib.h>

int main(int argc, char ** argv) {

    char * data_file = "../data/sin_110.wav";

    if (argc > 1) {
        data_file = argv[1];
    }

    audio_t audio;

    chaudio_create_audio_from_wav_file(&audio, data_file);

    chaudio_to_wav_fp(stdout, audio, CHAUDIO_WAVFMT_16I);

    chaudio_destroy_audio(&audio);

    return 0;
}



