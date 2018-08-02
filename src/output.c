
#include "chaudio.h"


#include <dlfcn.h>


chaudio_output_t chaudio_output_create(char * name, chaudio_OutputInit _init, chaudio_OutputDump _dump, chaudio_OutputFree _free, chaudio_paraminterface_t params) {
    chaudio_output_t out;
    out.name = malloc(strlen(name) + 1);
    strcpy(out.name, name);

    out.init = _init;
    out.dump = _dump;
    out.free = _free;

    out.params = params;

    out.output_data = NULL;

    return out;
}

int32_t chaudio_output_init(chaudio_output_t * output, int32_t channels, int32_t sample_rate) {
    output->channels = channels;
    output->sample_rate = sample_rate;

    void * _data = output->init(channels, sample_rate);
    output->output_data = _data;

    return (_data) == NULL;
}

int32_t chaudio_output_dump(chaudio_output_t * output, double * in, int32_t N) {
    return output->dump(output->output_data, in, N);
}

int32_t chaudio_output_free(chaudio_output_t * output) {
    return output->free(output->output_data);
}



/* loading outputs */


chaudio_output_t _output_load(char * file_name) {
    void * output_handle = dlopen(file_name, RTLD_NOW);

    if (output_handle == NULL) {
        // printf("chaudio: could not open plugin '%s': %s\n", file_name, dlerror());
        return (chaudio_output_t) { .name = NULL };
    }

    chaudio_output_t (*export_init_func)(chaudio_dl_init_t) = dlsym(output_handle, "chaudiooutput_export");

    char * result = dlerror();
    if (export_init_func == NULL || result != NULL) {
        //printf("chaudio: could not find plugin export (err='%s'), '%s' may be a generator or output\n", result, file_name);
        return (chaudio_output_t) { .name = NULL };
    }

    return export_init_func(chaudio_dl_init());
}

chaudio_output_t chaudio_output_load(char * file_name) {

    chaudio_output_t r = _output_load(file_name);

    if (CHAUDIO_OUTPUT_ISVALID(r)) {

        return r;
    } else if (getenv("CHAUDIO_PATH") != NULL) {

        char * chaudio_path = malloc(strlen(getenv("CHAUDIO_PATH")) + 1);

        strcpy(chaudio_path, getenv("CHAUDIO_PATH"));
        char * cur_check = malloc(strlen(chaudio_path) + strlen(file_name) + 4096 + 1);

        int i;
        char * cur_dir = strtok(chaudio_path, ":");
        
        while (cur_dir != NULL) {
            // different library naming conventions
            #ifdef __linux__
            sprintf(cur_check, "%s/outputs/lib%s.so", cur_dir, file_name);
            #endif

            #ifdef __APPLE__
            sprintf(cur_check, "%s/outputs/lib%s.dylib", cur_dir, file_name);
            #endif
            
            /*

            TODO: consider windows formatting for libraries

            */
            #ifdef _WINDOWS
            sprintf(cur_check, "%s/outputs/%s.dll", cur_dir, file_name);
            #endif

           // printf("checking file: '%s'\n" ,cur_check);
            r = _output_load(cur_check);

            if (CHAUDIO_OUTPUT_ISVALID(r)) {
                break;
            }

            cur_dir = strtok(NULL, ":");
        }
        free(cur_check);
        free(chaudio_path);

        if (CHAUDIO_OUTPUT_ISVALID(r)) return r;
    }

    return (chaudio_output_t) { .name = NULL };
}



