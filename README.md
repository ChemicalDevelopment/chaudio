
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


## Commandline

chaudio implements some commandline audio synthesis, processing, and workflow automation.

For instance:

`ch_signal -w square -s 0.75 -o - | ch_plugin -i - -E 5.0 -p delay -D delay=1.5 -D feedback=.2 -o test.wav`

Creates a short square wave, then echos it multiple times and outputs it to `test.wav`






