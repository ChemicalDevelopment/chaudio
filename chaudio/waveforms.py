"""

Source for generating waveforms (like sin, saw, square, etc)

In general, a function f should take in a time parameter `t` that can be either a normal float, or a numpy array, and `hz` should be able to be a constant or numpy array


"""

import chaudio

import numpy as np

def sin(t, hz, tweak=None):
    base_sin = np.sin((2 * np.pi * hz) * (t))
    if tweak is None:
        return base_sin
    else:
        signs = np.sign(base_sin)
        return signs * (np.abs(base_sin) ** (1 + tweak))

def saw(t, hz, tweak=None):
    base_saw = 2 * ((t * hz) % 1.0) - 1
    if tweak is None:
        return base_saw
    else:
        return base_saw * (1 + tweak * sin(t, hz, tweak))

def square(t, hz, tweak=None):
    if tweak is None:
        return 2 * (((t * hz) % 1.0) > .5) - 1
    else:
        return 2 * (((t * hz) % 1.0) > tweak) - 1

def triangle(t, hz, tweak=None):
    base_triangle = np.abs(4 * ((t * hz + .75) % 1.0) - 2) - 1
    if tweak is None:
        return base_triangle
    else:
        return base_triangle - .4 * tweak * triangle(t, hz, tweak=None) * square(t, hz, tweak)

def noise(t, hz=0, tweak=None):
    return 2 * np.random.ranf(len(t)) - 1

def zero(t, hz=0, tweak=None):
    return np.zeros((len(t),), dtype=np.float32)


