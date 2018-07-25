
# chaudio

chaudio is an audio library (chemicaldevelopment audio) in C with (planned) python bindings.

Meant to be mainly for signal manipulation rather than composing, but can be used that way programmatically.


Features:

  * Efficient python bindings
  * Implementations of common effects (filters, EQ, echo, delay, reverb, etc)
  * A programming language (similar to Csound, but more generalized) called `chlang`
  * Commandline based processing tools for fast workflows
  * Audio converter
  * Extendendable interface (so you can write your own processing in Python, C, chlang)


## Compiling

In the main directory, run `mkdir build && cd build`

Now, run `cmake ..`

Now, run `make`

It should be compiled!

Examples should be in `examples/` subfolder


## Commandline

chaudio implements some commandline audio synthesis, processing, and workflow automation.

For instance:

`ch_signal -w square -s 0.75 -o - | ch_plugin -i - -E 5.0 -p delay -D delay=1.5 -D feedback=.2 -o test.wav`

Creates a short square wave, then echos it multiple times and outputs it to `test.wav`


# API

For most C calls, the format for audio transformation is:

`audio_t chaudio_FUNC(audio_t input, ... , audio_t * output)`

And `output` can be `NULL`. If `output == NULL`, then audio is allocated to hold the result. If not, `*output` is ensured to have enough space to hold the result, and it is returned (and modified). So, the lines are equivelant:

```
// however it is created
audio_t a = chaudio_audio_create_...();

audio_t b;

// these two are the same
b = chaudio_gain(a, NULL);

b = chaudio_audio_create_blank();
chaudio_gain(a, &b);

```

Note that for the second example, `b` must be initialized!





