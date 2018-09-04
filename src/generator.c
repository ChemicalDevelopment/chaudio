
#include "chaudio.h"

#include <dlfcn.h>

chaudio_generator_t chaudio_generator_create(char * name, chaudio_GeneratorInit _init, chaudio_GeneratorGenerate _generate, chaudio_GeneratorFree _free, chaudio_paraminterface_t params) {
    chaudio_generator_t gen;
    gen.name = malloc(strlen(name) + 1);
    strcpy(gen.name, name);

    gen.init = _init;
    gen.generate = _generate;
    gen.free = _free;

    gen.params = params;

    gen.out = NULL;

    return gen;
}

int chaudio_generator_init(chaudio_generator_t * gen, int channels, int sample_rate) {
    gen->channels = channels;
    gen->sample_rate = sample_rate;

    void * _data = gen->init(channels, sample_rate);
    gen->generator_data = _data;

    return (_data) == NULL;
}

// generates and stores into gen->out
int chaudio_generator_generate(chaudio_generator_t * gen, int bufsize) {
    gen->out = realloc(gen->out, sizeof(double) * bufsize * gen->channels);
    gen->N = bufsize;
    return gen->generate(gen->generator_data, gen->out, bufsize);
}

int chaudio_generator_free(chaudio_generator_t * gen) {
    return gen->free(gen->generator_data);
}


/* loading */

chaudio_generator_t _generator_load(char * file_name) {
    void * generator_handle = dlopen(file_name, RTLD_NOW);

    if (generator_handle == NULL) {
        return (chaudio_generator_t) { .name = NULL };
    }

    chaudio_generator_t (*export_init_func)(chaudio_dl_init_t) = dlsym(generator_handle, "chaudiogenerator_export");

    char * result = dlerror();
    if (export_init_func == NULL || result != NULL) {
        //printf("chaudio: could not find plugin export (err='%s'), '%s' may be a generator or output\n", result, file_name);
        return (chaudio_generator_t) { .name = NULL };
    }

    return export_init_func(chaudio_dl_init());
}

chaudio_generator_t chaudio_generator_load(char * file_name) {

    chaudio_generator_t r = _generator_load(file_name);


    if (CHAUDIO_GENERATOR_ISVALID(r)) {
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
            sprintf(cur_check, "%s/generators/lib%s.so", cur_dir, file_name);
            #endif

            #ifdef __APPLE__
            sprintf(cur_check, "%s/generators/lib%s.dylib", cur_dir, file_name);
            #endif
            
            /*

            TODO: consider windows formatting for libraries

            */
            #ifdef _WINDOWS
            sprintf(cur_check, "%s/generators/%s.dll", cur_dir, file_name);
            #endif


            // printf("checking file: '%s'\n" ,cur_check);
            r = _generator_load(cur_check);

            if (CHAUDIO_GENERATOR_ISVALID(r)) {
                break;
            }

            cur_dir = strtok(NULL, ":");

        }
        free(cur_check);
        free(chaudio_path);

        if (CHAUDIO_GENERATOR_ISVALID(r)) return r;
    }

    return (chaudio_generator_t) { .name = NULL };
}




