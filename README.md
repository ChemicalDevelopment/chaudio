# chaudio

chaudio is a python module to programmatically create music.

chaudio contains audio processing utilities for converting audio, and applying effects to already generated songs


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

You need either version of python (2 and 3 work, 3 is recommended), as well as numpy, scipy, and matplotlib.

You can easily install with pip: 

either `pip install chaudio`, or, for python3, `pip3 install chaudio`



