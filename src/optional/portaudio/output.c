/* src/optional/portaudio/input.c - plugin to write to portaudio devices


*/


#define PLUGIN_NAME "chaudio.output_portaudio"

#include "chaudioplugin.h"

// required specifically, make sure this plugin is being linked
#include <portaudio.h>


PaError pa_err = paNoError;

#define IFERR(st, ex) if ((pa_err = (st)) != paNoError) { printf("portaudio[output] error: %s\n", Pa_GetErrorText(pa_err)); ex }

// data struct passed between functions
typedef struct _OutputData {
    
    // basic stuff about the incoming stream
    int32_t channels, sample_rate;


    // port audio data
    struct {

        PaStream * stream;
        PaStreamParameters stream_params;

        float * fmt_buf;

        bool has_started;

    } pa;


    int nsum;
    

} OutputData;



void * f_init(int32_t channels, int32_t sample_rate) {

    OutputData * data = malloc(sizeof(OutputData));

    data->nsum = 0;

    data->channels = channels;
    data->sample_rate = sample_rate;

    data->pa.fmt_buf = NULL;
   
    // initialization
    IFERR(Pa_Initialize(), {
        return NULL;
    })

    // default only for now
    if ((data->pa.stream_params.device = Pa_GetDefaultOutputDevice()) == paNoDevice) {
        printf("portaudio error: couldn't find default output device\n");
        return NULL;
    }

    // set params
    data->pa.has_started = false;
    data->pa.stream_params.channelCount = data->channels;
    data->pa.stream_params.sampleFormat = paFloat32; /* 32 bit floating point output */
    data->pa.stream_params.suggestedLatency = Pa_GetDeviceInfo(data->pa.stream_params.device)->defaultHighOutputLatency;
    data->pa.stream_params.hostApiSpecificStreamInfo = NULL; 

    IFERR(Pa_OpenStream(
        &data->pa.stream,
        NULL, /* no input */
        &data->pa.stream_params,
        data->sample_rate,
        0,
        paClipOff,      /* we won't output out of range samples so don't bother clipping them */
        NULL,
        data
    ), {
        printf("portaudio: Failed to open stream! Output probably doesn't exist!\n");
        return NULL;
    })

    return (void *)data;
}

int32_t f_set_double(void * _data, char * key, double val) {
    OutputData * data = (OutputData *)_data;

    return 1;
}

int32_t f_process(void * _data, double * in, double * out, int32_t N) {

    OutputData * data = (OutputData *)_data;

    int i, j;

    
    data->pa.fmt_buf = realloc(data->pa.fmt_buf, sizeof(float) * N);

    for (i = 0; i < N; ++i) {
        for (j = 0; j < data->channels; ++j) {
            // convert to floating point
            data->pa.fmt_buf[data->channels * i + j] = (float) in[data->channels * i + j];

            // also copy the output
            out[data->channels * i + j] = in[data->channels * i + j];
        }
    }

    // start the stream
    if (!data->pa.has_started) {
        IFERR(Pa_StartStream(data->pa.stream), {
            printf("portaudio: Failed to start stream!\n");
            return NULL;
        });

        data->pa.has_started = true;
    }

    IFERR(Pa_WriteStream(data->pa.stream, data->pa.fmt_buf, N), {
        exit(1);
    });


    return 0;
}

int32_t f_free(void * _data) {
    OutputData * data = (OutputData *)_data;
    IFERR(Pa_StopStream(data->pa.stream), {});
    IFERR(Pa_CloseStream(data->pa.stream), {});
    if (_data != NULL) free(_data);
    return 0;
}

chaudio_plugin_t register_plugin() {
    return chaudio_plugin_create(PLUGIN_NAME, f_init, f_process, f_set_double, f_free);
}

