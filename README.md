
# chaudio

chaudio is an audio manipulation library (chemicaldevelopment audio) in C, but a usable high-level interface with memory management (but still accessible and directly editable).

This is useful for transforming Audio to then send to other programs (for instance, `portaudio`), or perform automation on your existing audio files (for instance, join a list of `.wav` files into one larger one for use in an album video).

Meant to be mainly for signal manipulation and generation rather than composing music, but can be used that way programmatically (on the list of TODO is to create more musical functionality).

## Licensing

Chaudio is licensed under the LGPLv3. The `L` in `LGPL` means lesser, and this license allows proprietary code bases to use free software without having to release the source code for your program. See [here](https://softwareengineering.stackexchange.com/questions/86142/what-exactly-do-i-need-to-do-if-i-use-a-lgpl-licenced-library). TL;DR: Give credit to me to your users (attribution), and include a shared version of the library so it can be updated by the users.


## Features

  * Struct (`audio_t`) based Audio manipulation (you don't have to deal with buffers! Or worry about the lengths of allocated stuff!). All you have to call is methods.
  * Implementations of common effects (filters, EQ, echo, delay, reverb, etc)
  * A programming language (similar to Csound, but more generalized) called `chlang`
  * Commandline based processing tools for fast workflows
  * Audio converter
  * Extendendable interface (so you can write your own processing in Python, C, other languages)
  * Efficient python bindings (PLANNED)


## Compiling

In the main directory, run `mkdir build && cd build`

Now, run `cmake ..`

Now, run `make`

It should be compiled!

Examples should be in `examples/` subfolder

### Optional Dependencies

You can build `chaudio` with extensions that can be used for additional features. For instance, `portaudio` can be used for realtime audio processing with routing through devices. You would run `cmake .. -DWITH_PORTAUDIO=on` to require chaudio to be compiled with support. Here is a list of all extensions:

| Optional Dependency | Build Option | Features |
| [portaudio](http://www.portaudio.com/) | `-DWITH_PORTAUDIO=on` | Real time audio processing, audio device interface |




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

Note that for the second example, `b` must be initialized (which `chaudio_audio_create_blank()` does)!





