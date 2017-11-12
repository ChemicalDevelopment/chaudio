"""Waveform Generation Functions (:mod:`chaudio.waves`)
====================================================


.. currentmodule:: chaudio.waves

Source for calculating waveform values (like :meth:`chaudio.waves.sin`, :meth:`chaudio.waves.saw`, etc)

In general, all waveform functions ``f`` should take in a time parameter ``t`` that can be either a constant or a numpy array, and `hz` should be able to be a constant or numpy array. Also, they should accept an optional value called ``tweak``, which (if supported) should return a slightly different waveform based on the value of ``tweak``.

Note that ALL waveforms should accept this ``tweak`` value, even if they do nothing. This is for compatability 

Some other general rules (these are by no means required, however):

>>> f(0, hz) == 0
>>> f(t, hz, tweak=None) == f(t, hz)
>>> f(t+1.0/hz, hz) == f(t, hz)

The general idea with a waveform is that it repeats every ``1.0/hz`` seconds, and each oscillation (or cycle) is the exact same. 

Different frequencies have different pitches (see :meth:`chaudio.util.note`), and different waveforms have different timbres (pronounced ``TAM-BER`` or ``TIM-BER``). In fact, all instruments digital and real-world all are just different waveforms. Even when you play a guitar, it is simply a waveform played at a pitch.

These are generated on a non-continious (which is a synonym of discrete) sample array, each value in the sample array representing a point in time, and the amplitude of the sound at that point in time. These sample arrays, since they aren't continious, have a samplerate, or how many records it has per second. The most common value is 44100, that is, 44100 recordings are held per second of data. And, consequently, if our array is named ``ar``, ``ar[0]`` represents the sound's amplitude at time :math:`t = \\frac{0}{44100} = 0`` seconds. And, at ``ar[25000]``, it holds the amplitude at :math:`t = \\frac{25000}{44100} \\approx .566` seconds.

As we have said, the waveform repeats every :math:`\\frac{1}{hz}`` seconds, which means that it repeats :math:`hz` times per second. Thus, :math:`ar[0]` represents the start of the first waveform, and :math:`ar[\\left \\lfloor \\frac{44100}{hz} \\right \\rfloor]` marks the end of the first oscillation and the beginning of the second.


"""

import chaudio

import numpy as np

def sin(t, hz, tweak=None):
    """Computes the `sin wave <https://en.wikipedia.org/wiki/Sine_wave>`_ of sample times (``t``), and frequencies (``hz``)

    Optionally, if tweak is set, return a slightly modified waveform.

    With no tweak, the return value is :math:`sin(2 \pi * hz * t)`, but with the return value, :math:`sin(2 \pi * hz * t) ^ {1 + tweak}` is returned.

    Parameters
    ----------
    t : float, int, np.ndarray
        If a float or int, return the value of the sin wave at time ``t``, in seconds. If it is a numpy array, return an array of values at the sin wave corresponding to each time value in the array.
    
    hz : float, int, np.ndarray
        Frequency of wave. If the type of ``hz`` is np.ndarray, it must have the same shape as ``t``, and in that case each corresponding value of ``t``'s wave is assumed to have ``hz``'s value at the same index as the frequency value.

    tweak : float, int, np.ndarray
        A value to change the waveform. If the type of ``tweak`` is a numpy array, it must have the same shape as ``t``, and in that case each corresponding value of ``t``'s wave is assumed to have ``tweak``'s value at the same index as the tweak value (see examples below).

    Returns
    -------
    float, np.ndarray
        If all ``t``, ``hz``, and ``tweak`` are floats or ints, the function returns a float. Else, all parameters which are np.ndarray's must have the same shape, and the returned value is the same shape.

    Examples
    --------
    >>> t = 0
    >>> chaudio.waves.sin(t, 1)
    0.0
    >>> t = chaudio.times(5)
    >>> chaudio.waves.sin(t, 1)
    array([ 0.        ,  0.00014248,  0.00028495, ..., -0.00042743,
       -0.00028495, -0.00014248])

    See Also
    --------
    :meth:`chaudio.util.times` : returns sample times, which can be passed to this function as sample times

    """

    base_sin = np.sin((2 * np.pi * hz) * (t))
    if tweak is None:
        return base_sin
    else:
        signs = np.sign(base_sin)
        return signs * (np.abs(base_sin) ** (1 + tweak))

def saw(t, hz, tweak=None):
    """Computes the `sawtooth wave <https://en.wikipedia.org/wiki/Sawtooth_wave>`_ of sample times (``t``), and frequencies (``hz``)

    Optionally, if tweak is set, return a slightly modified waveform.

    With no tweak, the return value is :math:`saw(2 \pi * hz * t)`, but with the return value, :math:`saw(2 \pi * hz * t) * (1 + tweak * sin(t, hz, tweak))` is returned.

    This has the effect of making the waveform appear "bendy", but still resemble a sawtooth.

    Parameters
    ----------
    t : float, int, np.ndarray
        If a float or int, return the value of the sawtooth wave at time ``t``, in seconds. If it is a numpy array, return an array of values at the sawtooth wave corresponding to each time value in the array.
    
    hz : float, int, np.ndarray
        Frequency of wave. If the type of ``hz`` is np.ndarray, it must have the same shape as ``t``, and in that case each corresponding value of ``t``'s wave is assumed to have ``hz``'s value at the same index as the frequency value.

    tweak : float, int, np.ndarray
        A value to change the waveform. If the type of ``tweak`` is a numpy array, it must have the same shape as ``t``, and in that case each corresponding value of ``t``'s wave is assumed to have ``tweak``'s value at the same index as the tweak value (see examples below).

    Returns
    -------
    float, np.ndarray
        If all ``t``, ``hz``, and ``tweak`` are floats or ints, the function returns a float. Else, all parameters which are np.ndarray's must have the same shape, and the returned value is the same shape.

    Examples
    --------
    >>> t = 0
    >>> chaudio.waves.saw(t, 1)
    0.0
    >>> t = chaudio.times(5)
    >>> chaudio.waves.saw(t, 1)
    array([  0.00000000e+00,   4.53514739e-05,   9.07029478e-05, ...,
        -1.36054422e-04,  -9.07029478e-05,  -4.53514739e-05])


    See Also
    --------
    :meth:`chaudio.util.times` : returns sample times, which can be passed to this function as sample times

    """
    base_saw = 2 * ((t * hz + .5) % 1.0) - 1
    if tweak is None:
        return base_saw
    else:
        return base_saw * (1 + tweak * sin(t, hz, tweak))

def square(t, hz, tweak=None):
    """Computes the `square wave <https://en.wikipedia.org/wiki/Square_wave>`_ of sample times (``t``), and frequencies (``hz``)

    Optionally, if tweak is set, return a slightly modified waveform.

    With no tweak, the return value is :math:`square(2 \pi * hz * t)`, which has a `duty cycle <https://en.wikipedia.org/wiki/Duty_cycle>`_ of ``50%``, or ``.5``. If set, the duty cycle is set to ``tweak``, and if ``tweak==.5``, that results in a normal square wave.

    This has similar effects to opening up an envelope


    Parameters
    ----------
    t : float, int, np.ndarray
        If a float or int, return the value of the square wave at time ``t``, in seconds. If it is a numpy array, return an array of values at the square wave corresponding to each time value in the array.
    
    hz : float, int, np.ndarray
        Frequency of wave. If the type of ``hz`` is np.ndarray, it must have the same shape as ``t``, and in that case each corresponding value of ``t``'s wave is assumed to have ``hz``'s value at the same index as the frequency value.

    tweak : float, int, np.ndarray
        A value to change the waveform. If the type of ``tweak`` is a numpy array, it must have the same shape as ``t``, and in that case each corresponding value of ``t``'s wave is assumed to have ``tweak``'s value at the same index as the tweak value (see examples below).

    Returns
    -------
    float, np.ndarray
        If all ``t``, ``hz``, and ``tweak`` are floats or ints, the function returns a float. Else, all parameters which are np.ndarray's must have the same shape, and the returned value is the same shape.

    Notes
    -----

    Unlike most other waveforms, the square wave starts at ``-1``, whereas most start at ``0``. However, since the square wave only has values taking either ``-1`` or ``+1`` (even in modified form), this is done as a compromise

    Examples
    --------
    >>> t = 0
    >>> chaudio.waves.square(t, 1)
    -1
    >>> t = chaudio.times(5)
    >>> chaudio.waves.saw(t, 1)
    array([-1, -1, -1, ...,  1,  1,  1])


    See Also
    --------
    :meth:`chaudio.util.times` : returns sample times, which can be passed to this function as sample times
    `Pulse wave <https://en.wikipedia.org/wiki/Pulse_wave>`_ : with a modified tweak value, the waveform is a Pulse wave with duty cycle equal to ``tweak``

    """

    if tweak is None:
        return 2 * (((t * hz) % 1.0) > .5) - 1
    else:
        return 2 * (((t * hz) % 1.0) > tweak) - 1

def triangle(t, hz, tweak=None):
    """Computes the `triangle wave <https://en.wikipedia.org/wiki/Triangle_wave>`_ of sample times (``t``), and frequencies (``hz``)

    Optionally, if tweak is set, return a slightly modified waveform.

    With no tweak, the return value is :math:`triangle(2 \pi * hz * t)`, which looks like a sin wave, except it is straight lines.

    With a tweak value, :math:`triangle(2 \pi * hz * t) - tweak * saw(2 \pi * hz * t) * square(2 \pi * hz * t, tweak)` is returned, which can generate a lot of different timbres. In the future, I'll add an in depth description of what kind of sounds this creates.


    Parameters
    ----------
    t : float, int, np.ndarray
        If a float or int, return the value of the triangle wave at time ``t``, in seconds. If it is a numpy array, return an array of values at the triangle wave corresponding to each time value in the array.
    
    hz : float, int, np.ndarray
        Frequency of wave. If the type of ``hz`` is np.ndarray, it must have the same shape as ``t``, and in that case each corresponding value of ``t``'s wave is assumed to have ``hz``'s value at the same index as the frequency value.

    tweak : float, int, np.ndarray
        A value to change the waveform. If the type of ``tweak`` is a numpy array, it must have the same shape as ``t``, and in that case each corresponding value of ``t``'s wave is assumed to have ``tweak``'s value at the same index as the tweak value (see examples below).

    Returns
    -------
    float, np.ndarray
        If all ``t``, ``hz``, and ``tweak`` are floats or ints, the function returns a float. Else, all parameters which are np.ndarray's must have the same shape, and the returned value is the same shape.

    Notes
    -----

    Unlike most other waveforms, the square wave starts at ``-1``, whereas most start at ``0``. However, since the square wave only has values taking either ``-1`` or ``+1`` (even in modified form), this is done as a compromise

    Examples
    --------
    >>> t = 0
    >>> chaudio.waves.triangle(t, 1)
    0.0
    >>> t = chaudio.times(5)
    >>> chaudio.waves.triangle(t, 1)
    array([  0.00000000e+00,   9.07029478e-05,   1.81405896e-04, ...,
        -2.72108844e-04,  -1.81405896e-04,  -9.07029478e-05])


    See Also
    --------
    :meth:`chaudio.util.times` : returns sample times, which can be passed to this function as sample times

    """

    base_triangle = np.abs(4 * ((t * hz + .75) % 1.0) - 2) - 1
    if tweak is None:
        return base_triangle
    else:
        return base_triangle - tweak * saw(t, hz) * square(t, hz, tweak)

# returns random noise (white noise)
def noise(t, hz=0, tweak=None):
    return 2 * np.random.ranf(len(t)) - 1

# returns zeros
def zero(t, hz=0, tweak=None):
    return np.zeros((len(t),), dtype=np.float32)


