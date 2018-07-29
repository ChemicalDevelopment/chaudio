
/*

profiles common operations

*/



#include "chaudio.h"

#include <stdio.h>
#include <stdlib.h>


/*


*/

#ifdef __linux__
# include <sys/sysinfo.h>
#endif

#ifdef __APPLE__
# include <mach/task.h>
# include <mach/mach_init.h>
#endif

#ifdef _WINDOWS
# include <windows.h>
#else
# include <sys/resource.h>
#endif

/// The amount of memory currently being used by this process, in bytes.
/// By default, returns the full virtual arena, but if resident=true,
/// it will report just the resident set in RAM (if supported on that OS).
size_t memory_used ()
{
#if defined(__linux__)
    // Ugh, getrusage doesn't work well on Linux.  Try grabbing info
    // directly from the /proc pseudo-filesystem.  Reading from
    // /proc/self/statm gives info on your own process, as one line of
    // numbers that are: virtual mem program size, resident set size,
    // shared pages, text/code, data/stack, library, dirty pages.  The
    // mem sizes should all be multiplied by the page size.
    size_t size = 0;
    FILE *file = fopen("/proc/self/statm", "r");
    if (file) {
        unsigned long vm = 0;
        fscanf (file, "%ul", &vm);  // Just need the first num: vm size
        fclose (file);
       size = (size_t)vm * getpagesize();
    }
    return size;

#elif defined(__APPLE__)
    // Inspired by:
    // http://miknight.blogspot.com/2005/11/resident-set-size-in-mac-os-x.html
    struct task_basic_info t_info;
    mach_msg_type_number_t t_info_count = TASK_BASIC_INFO_COUNT;
    task_info(current_task(), TASK_BASIC_INFO, (task_info_t)&t_info, &t_info_count);
    return t_info.resident_size;

#elif defined(_WINDOWS)
    // According to MSDN...
    PROCESS_MEMORY_COUNTERS counters;
    if (GetProcessMemoryInfo (GetCurrentProcess(), &counters, sizeof (counters)))
        return counters.PagefileUsage;
    else return 0;

#else
    // No idea what platform this is
    return 0;   // Punt
#endif
}


#define MEM_MB (((double)memory_used()) / (1024.0 * 1024.0))

int main(int argc, char ** argv) {

    chaudio_init();
    printf("%s\n", chaudio_get_build_info());

    // how many trials of each test are we going to do?
    int32_t num_trials = 10;
    // how many samples all trials are of (do 10 seconds)
    int64_t N_samples = CHAUDIO_DEFAULT_SAMPLE_RATE * 10;
    int32_t i;

    // timing variables useda
    double st, et;

    // audio buffers used , 1 for each trial
    audio_t *a = malloc(sizeof(audio_t) * num_trials), *b = malloc(sizeof(audio_t) * num_trials), *c = malloc(sizeof(audio_t) * num_trials);


    printf("beginning trials (doing %d of each) with %d samples (%lf seconds of data)\n", num_trials, N_samples, (double)N_samples/CHAUDIO_DEFAULT_SAMPLE_RATE);

    /* creation */
    st = chaudio_time();
    for (i = 0; i < num_trials; ++i) {
        a[i] = chaudio_audio_create(N_samples, 1, CHAUDIO_DEFAULT_SAMPLE_RATE);
    }
    et = (chaudio_time() - st) / num_trials;

    double baseline_mem = MEM_MB;

    printf("current memory being used %lf Mb\n", baseline_mem);

    printf("creation avg: %.2lf ms\n", et * 1000.0);

    /* signal generation (sin) */
    st = chaudio_time();
    for (i = 0; i < num_trials; ++i) {
        chaudio_signal_generate(&a[i], CHAUDIO_WAVEFORM_SIN, 220.0, 0.0);
    }

    et = (chaudio_time() - st) / num_trials;
    printf("generation (sin) avg: %.2lf ms\n", et * 1000.0);


    /* signal generation (square) */
    st = chaudio_time();
    for (i = 0; i < num_trials; ++i) {
        chaudio_signal_generate(&a[i], CHAUDIO_WAVEFORM_SQUARE, 220.0, 0.0);
    }

    et = (chaudio_time() - st) / num_trials;
    printf("generation (square) avg: %.2lf ms\n", et * 1000.0);


    /* signal generation (noise) */
    st = chaudio_time();
    for (i = 0; i < num_trials; ++i) {
        chaudio_signal_generate(&a[i], CHAUDIO_WAVEFORM_NOISE, 220.0, 0.0);
    }

    et = (chaudio_time() - st) / num_trials;
    printf("generation (noise) avg: %.2lf ms\n", et * 1000.0);


    /* gain (+0db) */
    st = chaudio_time();
    for (i = 0; i < num_trials; ++i) {
        chaudio_gain(a[i], 0.0, &a[i]);
    }

    et = (chaudio_time() - st) / num_trials;
    printf("gain (+0db) avg: %.2lf ms\n", et * 1000.0);

    /* gain (+10db) */
    st = chaudio_time();
    for (i = 0; i < num_trials; ++i) {
        chaudio_gain(a[i], 10.0, &a[i]);
    }

    et = (chaudio_time() - st) / num_trials;
    printf("gain (+10db) avg: %.2lf ms\n", et * 1000.0);


    /* gain (-10db) */
    st = chaudio_time();
    for (i = 0; i < num_trials; ++i) {
        chaudio_gain(a[i], -10.0, &a[i]);
    }

    et = (chaudio_time() - st) / num_trials;
    printf("gain (-10db) avg: %.2lf ms\n", et * 1000.0);

    /* gain (+10db) */
    st = chaudio_time();
    for (i = 0; i < num_trials; ++i) {
        chaudio_gain(a[i], 10.0, &a[i]);
    }

    et = (chaudio_time() - st) / num_trials;
    printf("gain (10db) avg: %.2lf ms\n", et * 1000.0);


    printf("additional memory used: %lf Mb (anything less than 1Mb is OK)\n", MEM_MB - baseline_mem);


    return 0;
}


