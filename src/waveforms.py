"""

Source for generating waveforms (like sin, saw, square, etc)

In general, a function f should take in a time parameter `t` that can be either a normal float, or a numpy array, and `hz` should be able to be a constant or numpy array


"""

import numpy as np


def sin(t, hz):
    return np.sin(2 * np.pi * (t) * (hz))

def saw(t, hz):
    return 2 * ((t * hz) % 1.0) - 1

def square(t, hz):
    return 2 * (((t * hz) % 1.0) > .5) - 1

def triangle(t, hz):
    return 1 - 2 * ((2 * ((t * hz) % 1.0) - 1).__abs__())



