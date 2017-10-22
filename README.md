# chaudio

chaudio is a collection of audio processing tools


## Usage

### simple.py

Run `python3 src/simple.py` to create `simple.wav`, and showcase basis synthesis with chaudio

### read.py

This allows you to perform analysis on existing sound files

Run `python3 src/read.py -h` for help.

Once you've ran `simple.py`, you will have `simple.wav`, which you can use with this example:

`python3 src/read.py simple.wav -g freq`

to show a frequency graph of the sound


## Installation

You need `python3`, and will need numpy, matplotlib, and other dependencies.

Just run `pip3 install -r requirements.txt` to install all python dependencies.



