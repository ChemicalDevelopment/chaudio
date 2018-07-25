/*

util.h - basic utilities

*/


#ifndef __UTIL_H__
#define __UTIL_H__
// useful macros

#define CHAUDIO_IS_MONO(au) ((au).channels == 1)
#define CHAUDIO_IS_STEREO(au) ((au).channels == 2)

#define CHAUDIO_ARE_SAME(a, b) ((a).data == (b).data && !((a).data == NULL || (b).data == NULL))


#define S_PER_MS (0.001)
#define MS_PER_S (1000)

#define GAIN_COEF(db) (pow(10.0, (db) / 20.0))


// returns min_val if x < min_val and max_val if x > max_val, and x otherwise
double double_limit(double x, double min_val, double max_val);


// gets the length in seconds (computed using length and sample_rate)
double chaudio_audio_duration(audio_t audio);


// these return a pointer.
// call them with `output == NULL` and have it automatically allocate the result and return the pointer to it.
// if this happens, you MUST free the result or will have memory leaks.
// But, if a valid pointer to audio_t is given, it does not allocate more (except for reallocating for different sizes)

// most can be called with "chaudio_copy(a, a)"
// and should detect if it is in place
// if this is the case, then the `a` is freed, and should not be used anymore!

// output is NULL-able
audio_t chaudio_copy(audio_t input, audio_t * output);

audio_t chaudio_resample(audio_t input, int64_t new_sample_rate, audio_t * output);

// sums all channels and divides by the number of channels
audio_t chaudio_mix_to_mono(audio_t input, audio_t * output);

// scales all values by a factor so that abs(input) <= 1.0 for all values
audio_t chaudio_normalize(audio_t input, audio_t * output);

// gains the audio
audio_t chaudio_gain(audio_t input, double db, audio_t * output);

// adjusts to a new length
audio_t chaudio_adjust_length(audio_t input, int64_t to_length, audio_t * output);

// pad, add extra zeros
audio_t chaudio_pad(audio_t input, int64_t num_zeros, audio_t * output);

// appends them together
audio_t chaudio_append(audio_t input_A, audio_t input_B, audio_t * output);

#endif


