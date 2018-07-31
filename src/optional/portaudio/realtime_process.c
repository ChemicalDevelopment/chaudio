
/*

specific code to realtime process inputs and whatnot

*/


/* src/optional/portaudio/input.c - plugin to read portaudio devices


*/


#include "chaudio.h"

#ifndef HAVE_PORTAUDIO
#error Need portaudio for this
#endif

// required specifically, make sure this plugin is being linked
#include <portaudio.h>

PaError pa_err;

#define IFERR(st, ex) if ((pa_err = (st)) != paNoError) { printf("portaudio[realtime_process] error: %s\n", Pa_GetErrorText(pa_err)); ex }


typedef struct pa_data_t {

    int32_t channels, sample_rate;

    chaudio_pipeline_t * pipeline;

    double * in, * out;

} pa_data_t;


void _pa_streamfinished(void *userData) {
    printf("stream finished!\n");
}

int _pa_callback(
    const float * in, float * out,
    unsigned long N,
    const PaStreamCallbackTimeInfo* timeInfo,
    PaStreamCallbackFlags statusFlags,
    void * _data
) {
    
    pa_data_t * data = (pa_data_t *)_data;

    data->in = realloc(data->in, sizeof(double) * N * data->channels);
    data->out = realloc(data->out, sizeof(double) * N * data->channels);

    int i;
    // convert into double format
    for (i = 0; i < N * data->channels; ++i) {
        data->in[i] = (double) in[i];
        if (data->pipeline->plugins_len == 0) data->out[i] = (double) in[i];
    }

    void * _tmp; // for swapping

    double st = chaudio_time();

    for (i = 0; i < data->pipeline->plugins_len; ++i) {
        chaudio_plugin_t cplg = data->pipeline->plugins[i];
        if (i != 0) {
            _tmp = data->out;
            data->in = data->out;
            data->out = _tmp;
        }
        
        cplg.process(cplg.plugin_data, data->in, data->out, N);
    }

    double et = chaudio_time();

    // output to float
    for (i = 0; i < N * data->channels; ++i) {
        out[i] = (float) data->out[i];
    }

    return paContinue;
}

void chaudio_portaudio_realtime_process(chaudio_pipeline_t * pipeline, int32_t bufsize) {

    int channels = 1;

    // initialization
    IFERR(Pa_Initialize(), {
        printf("error initializing\n");
    })

    PaStream * stream;
    PaStreamParameters input_params, output_params;

    // default only for now
    if ((input_params.device = Pa_GetDefaultInputDevice()) == paNoDevice) {
        printf("portaudio error: couldn't find default input device\n");
    }

    // set params
    input_params.channelCount = channels;
    input_params.sampleFormat = paFloat32; /* 32 bit floating point output */
    input_params.suggestedLatency = Pa_GetDeviceInfo(input_params.device)->defaultLowInputLatency;
    input_params.hostApiSpecificStreamInfo = NULL; 

    // default only for now
    if ((output_params.device = Pa_GetDefaultOutputDevice()) == paNoDevice) {
        printf("portaudio error: couldn't find default output device\n");
    }

    // set params
    output_params.channelCount = channels;
    output_params.sampleFormat = paFloat32; /* 32 bit floating point output */
    output_params.suggestedLatency = Pa_GetDeviceInfo(output_params.device)->defaultLowOutputLatency;
    output_params.hostApiSpecificStreamInfo = NULL; 


    pa_data_t pa_data;

    pa_data.channels = channels;
    pa_data.sample_rate = CHAUDIO_DEFAULT_SAMPLE_RATE;
    pa_data.in = NULL;
    pa_data.out = NULL;
    pa_data.pipeline = pipeline;

    IFERR(Pa_OpenStream(
        &stream,
        &input_params,
        &output_params,
        44100,
        bufsize, // we use output stuff
        paClipOff, /* we won't output out of range samples so don't bother clipping them */
        _pa_callback,
        &pa_data
    ), {
        printf("portaudio: Failed to open stream! Input probably doesn't exist!\n");
    })


    IFERR(Pa_SetStreamFinishedCallback(stream, &_pa_streamfinished), {
        printf("portaudio: Failed to set stream finish callback\n");
    })

    // start the stream

    IFERR(Pa_StartStream(stream), {
        printf("portaudio: Failed to start stream!\n");
    });


    while (1) ;

    IFERR(Pa_StopStream(stream), {});
    IFERR(Pa_CloseStream(stream), {});

}

