
#include "chaudio.h"

#include <stdlib.h>

// getopt
#include <unistd.h>

#include <string.h>


int main(int argc, char ** argv) {

    chaudio_init();

    // what is our input/output?
    char * output_file = NULL;

    int i;
    char c;

    double gain = -1.0;
    double hz = 110;

    double duration = 2.5;
    
    int waveform = CHAUDIO_WAVEFORM_SIN;
    int sample_rate = CHAUDIO_DEFAULT_SAMPLE_RATE;

    while ((c = getopt (argc, argv, "o:g:f:s:w:h")) != (char)-1) {
        if (c == 'h') {
            printf("chaudio signal generator\n");
            printf("Usage: signal [options...] [input]\n");
            printf("\n");
            printf("  -o [file]   output file (if nothing, uses stdout)\n");
            printf("  -s [sec]    duration");
            printf("  -f [hz]     frequency\n");
            printf("  -w [WAVE]   waveform (sin,square)");
            printf("  -g [n]      decibels volume\n");
            printf("  -h          show this help message\n");
            printf("\n");
            return 0;
        } else if (c == 'g') {
            sscanf(optarg, "%lf", &gain);
        } else if (c == 's') {
            sscanf(optarg, "%lf", &duration);
        } else if (c == 'f') {
            sscanf(optarg, "%lf", &hz);
        } else if (c == 'w') {
            if (strcmp(optarg, "sin") == 0) {
                waveform = CHAUDIO_WAVEFORM_SIN;
            } else if (strcmp(optarg, "square") == 0) {
                waveform = CHAUDIO_WAVEFORM_SQUARE;
            } else {
                fprintf(stderr, "ERROR: invalid waveform\n");
                return 1;
            }
        } else if (c == 'o') {
            output_file = optarg;
        } else {
            printf("ERROR: incorrect argument: -%c\n", optopt);
            return 1;
        }
    }


    audio_t audio = chaudio_audio_create((int64_t)floor(sample_rate * duration), 1, sample_rate);

    chaudio_signal_generate(&audio, waveform, hz, 0.0);

    audio_t res = chaudio_gain(audio, gain, NULL);

    // output it
    if (output_file == NULL || strcmp(output_file, "-") == 0) {
        
        chaudio_audio_output_wav_fp(stdout, res, CHAUDIO_WAVFMT_16I);
    } else {
        chaudio_audio_output_wav(output_file, res, CHAUDIO_WAVFMT_16I);
    }


    chaudio_audio_free(&audio);
    chaudio_audio_free(&res);

    return 0;
}



