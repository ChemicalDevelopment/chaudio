# chaudio

chaudio is a collection of audio processing tools


## Usage

### ex_simple.py

Run `python3 src/ex_simple.py` to create `simple.wav`, and showcase basis synthesis with chaudio


### ex_read.py

This allows you to perform analysis on existing sound files

Run `python3 src/ex_read.py -h` for help.

Once you've ran `ex_simple.py`, you will have `simple.wav`, which you can use with this example:

`python3 src/ex_read.py simple.wav -g freq`

to show a frequency graph of the sound


### ex_waveform.py

Use this to test out various waveforms:

`python3 src/ex_waveform.py -w "wf.saw(t, hz, 0.78)" -g`

the `-w` option refers to the wave generation. Complete this with `t`, `hz` and then an (optional) tweak value


### ex_compose.py

This is more in depth, how to use arrangers to string together notes, and use plugins


## Installation

You need `python3`, and will need numpy, matplotlib, and other dependencies.

Just run `pip3 install -r requirements.txt` to install all python dependencies.



