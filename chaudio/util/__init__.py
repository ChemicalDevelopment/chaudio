"""
.. currentmodule:: chaudio.util

Utility Functions (:mod:`chaudio.util`)
=======================================

This module provides useful utilities and classes to be used elsewhere. Note that most of these functions are aliased directly to the main :mod:`chaudio` module. Ones that are not aliased are often lower level and may not support all input types.



Utility Classes
---------------

.. autosummary::
    :toctree: classes

    TimeSignature


Utility Functions
-----------------

.. autosummary::
    :toctree: functions

    times
    normalize

DONE

"""

import numpy as np

import chaudio
import chaudio.util.freq


# returns array of sample times
# if a time (in seconds) is returned, the default hz value from chaudio.defaults is taken if hz==None
# if it's a source, we get how many seconds it lasts, and duplicate an array that would fit it
def times(t, hz=None):
    """

    Returns an array representing time values of samples.

    :param t: A value representing a number of seconds
    :type t: float, int, numpy array, chaudio.source.Source
    :rtype: a numpy array

    """
    
    _t = None
    if hz is None:
        if issubclass(type(t), chaudio.source.Source):
            hz = v.hz
            _t = v.seconds
        elif type(t) is np.ndarray:
            hz = chaudio.defaults["hz"]
            _t = len(v) / hz
        else:
            hz = chaudio.defaults["hz"]

    if _t is None:
        _t = t

    return np.arange(0, _t, 1.0 / hz)

# returns smallest normalization factor, such that -1.0<=v/normalize_factor(v)<=1.0, for all values in the array
def normalize_factor(v):
    if issubclass(type(v), chaudio.source.Source):
        return max([normalize_factor(i) for i in v.data])
    elif type(v) is np.ndarray:
        return np.max(np.abs(v))
    else:
        raise Exception("don't know how to normalize '%s'" % type(v).__name__)

# returns a normalized vector
def normalize(v):
    fact = normalize_factor(v)
    if fact == 0:
        return v
    else:
        return v / fact


class TimeSignature:
    """

    Represents a `time signature <https://en.wikipedia.org/wiki/Time_signature>`_.

    """

    def __init__(self, beats, division, bpm=80):
        """
        Initializes the timesignature to have ``beats`` number of pulses per measure, with the note represented as ``division`` getting a single beat.

        If division is 4, the quarter note gets the beat, 8 means the 8th note gets the beat, etc

        :param beats: The number of beats (or pulses) per measure
        :type beats: int, float
        :param division: The note division that represents a single pulse
        :type division: int, float
        :param bpm: The speed, in beats per minute
        :type bpm: int, float (optional)

        """

        self.bpm = bpm
        self.beats = beats
        self.division = division


    def __getitem__(self, key):
        """
        Returns the time in seconds of a number of beats, or a number of measures and beats.

        (this method is an alias for subscripting, so ``tsig.__getitem__(key)`` is equivelant to ``tsig[key]``)

        If ``key`` is a tuple, return the number of seconds that is equivalant to ``key[0]`` measures, and ``key[1]`` beats.

        In all cases, ``tsig[a] == tsig[a//tsig.beats, a%tsig.beats]``.

        When calling using a ``key`` that is a tuple, ``key[1]`` must not exceed the number of beats. This is to prevent errors arising from improper lengths. However, the number of beats can be any non-negative value if using a key that is a float or int.

        :param key: Either a tuple containing (measure, beat), or a number of beats
        :type key: int, float, or tuple
        :rtype: float

        """
        if type(key) not in (tuple, float, int):
            raise KeyError("TimeSignature key should be tuple (timesig[a,b] or timesig[a])")

        if type(key) is tuple:
            measure, beat = key
            if beat >= self.beats:
                raise ValueError("beat for time signature should be less than the number of beats in a measure, when using a tuple of (measure, beat) (err %s >= %s)" % (beat, self.beats))
        else:
            measure, beat = divmod(key, self.beats)

        if measure < 0:
            raise ValueError("measure for time signature should be positive (err %s < 0)" % (measure))

        if beat < 0:
            raise ValueError("beat for time signature should be positive (err %s < 0)" % (beat))

        return 60.0 * (self.beats * measure + beat) / self.bpm
    

    # so you can print out time signatures
    def __str__(self):
        return "%d/%d" % (self.beats, self.division)

    __repr__ = __str__





