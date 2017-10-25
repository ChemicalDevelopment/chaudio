# chaudio

chaudio is a collection of audio processing tools


## Usage

### Examples

Located in `examples/`, multiple example use cases of chaudio are shown.

To run with the development version of chaudio, prepend the PYTHONPATH environment.

`PYTHONPATH=$PWD python3 examples/{FILE}`

Or, if chaudio is installed, just run:

`python3 examples/{FILE}`

#### examples/simple.py

This creates a WAV file (`simple.wav`) that contains 5 seconds of the note A4 as a sin waveform.

#### examples/addnoise.py

This takes an input, and an optional output (default is `addnoise.wav`). 

It reads in a file, adds static, then outputs the result to output.

Run like `python3 examples/addnoise.py simple.wav -o simple_static.wav` (assuming you've ran `examples/simple.py`).


#### examples/compose.py

This example shows how to create an entire song, efficiently and rubustly.


## Installation

You need `python3`, and will need numpy, matplotlib, and other dependencies.

Just run `pip3 install -r requirements.txt` to install all python dependencies.



