"""
.. currentmodule:: chaudio.waves


Waveform Generation Functions (:mod:`chaudio.waves`)
====================================================

Source for calculating waveform values (like :meth:`chaudio.waves.sin`, :meth:`chaudio.waves.saw`, etc)

In general, all waveform functions ``f`` should take in a time parameter ``t`` that can be either a constant or a numpy array, and `hz` should be able to be a constant or numpy array. Also, they should accept an optional value called ``tweak``, which (if supported) should return a slightly different waveform based on the value of ``tweak``.

Note that ALL waveforms should accept this ``tweak`` value, even if they do nothing. This is for compatability 

Some other general rules (these are by no means required, however):

>>> f(0, hz) == 0
>>> f(t, hz, tweak=None) == f(t, hz)
>>> f(t+1.0/hz, hz) == f(t, hz)


Waveform Function Documentation
-------------------------------

.. autosummary::
   :toctree: functions

   sin
   saw
   square


"""

import chaudio

import numpy as np

def sin(t, hz, tweak=None):
    """
    Computes the `sin wave <https://en.wikipedia.org/wiki/Sine_wave>`_ of sample times (``t``), and frequencies (``hz``). Optionally, if tweak is set, return a slightly modified waveform.

    With no tweak, the return value is :math:`sin(2 \pi * hz * t)`, but with the return value, :math:`sin(2 \pi * hz * t) ^ {1 + tweak}` is returned.

    :param t: Time sample value. If it is a float or int, return the value of the sin wave at that time, in seconds. If it is a numpy array, return an array of values at the sin wave corresponding to each time value in the array.
    :type t: float, int, or numpy array
    :param hz: Frequency of sine wave. If the type of ``tweak`` is a numpy array, it must have the same shape as ``t``, and in that case each corresponding value of ``t``'s wave is assumed to have ``hz``'s value at the same index as the frequency value (see examples below).
    :type hz: float, int, or numpy array
    :param tweak: A value to change the waveform. If the type of ``tweak`` is a numpy array, it must have the same shape as ``t``, and in that case each corresponding value of ``t``'s wave is assumed to have ``tweak``'s value at the same index as the tweak value (see examples below).
    :type tweak: float, int, or numpy array
    :rtype: The same type that ``t`` was passed in

    Examples
    --------
    >>> t = 0
    >>> chaudio.waves.sin(t, 1)
    0.0

    in this example, the value of the wave at :math:`t=0` and a frequency of :math:`hz=1` is :math:`0.0`

    See Also
    --------
    :meth:`chaudio.util.times` : returns sample times

    >>> t = chaudio.times(2.5, )

    """

    base_sin = np.sin((2 * np.pi * hz) * (t))
    if tweak is None:
        return base_sin
    else:
        signs = np.sign(base_sin)
        return signs * (np.abs(base_sin) ** (1 + tweak))

# saw tooth wave /|/|/|
def saw(t, hz, tweak=None):
    base_saw = 2 * ((t * hz + .5) % 1.0) - 1
    if tweak is None:
        return base_saw
    else:
        return base_saw * (1 + tweak * sin(t, hz, tweak))

# square wave _|-_|-_|-
def square(t, hz, tweak=None):
    if tweak is None:
        return 2 * (((t * hz) % 1.0) > .5) - 1
    else:
        return 2 * (((t * hz) % 1.0) > tweak) - 1

# triangle wave /\/\/\
def triangle(t, hz, tweak=None):
    base_triangle = np.abs(4 * ((t * hz + .75) % 1.0) - 2) - 1
    if tweak is None:
        return base_triangle
    else:
        return base_triangle - .4 * tweak * triangle(t, hz, tweak=None) * square(t, hz, tweak)

# returns random noise (white noise)
def noise(t, hz=0, tweak=None):
    return 2 * np.random.ranf(len(t)) - 1

# returns zeros
def zero(t, hz=0, tweak=None):
    return np.zeros((len(t),), dtype=np.float32)


