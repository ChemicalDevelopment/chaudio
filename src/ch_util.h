/*

util.h - basic utilities

*/


#ifndef __UTIL_H__
#define __UTIL_H__

// returns min_val if x < min_val and max_val if x > max_val, and x otherwise
double double_limit(double x, double min_val, double max_val);

// these return a pointer.
// call them with `output == NULL` and have it automatically allocate the result and return the pointer to it.
// if this happens, you MUST free the result or will have memory leaks.
// But, if a valid pointer to audio_t is given, it does not allocate more (except for reallocating for different sizes)


audio_t * chaudio_copy(audio_t * output, audio_t input);

audio_t * chaudio_resample(audio_t * output, audio_t input, int new_sample_rate);

#endif


