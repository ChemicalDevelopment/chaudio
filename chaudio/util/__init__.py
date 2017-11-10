"""Utility Functions (:mod:`chaudio.util`)
=======================================


.. currentmodule:: chaudio.util

This module provides useful utilities and classes to be used elsewhere. Note that most of these functions are aliased directly to the main :mod:`chaudio` module. Ones that are not aliased are often lower level and may not support all input types.


"""

import numpy as np

import chaudio


valid_note_names = {
    "Ab": 25.95654359874657, 
    "A": 27.5, 
    "A#": 29.13523509488062, 
    "Bb": 29.13523509488062, 
    "B": 30.867706328507758, 
    "C": 32.70319566257483,
    "C#": 34.64782887210901, 
    "Db": 34.64782887210901, 
    "D": 36.70809598967595, 
    "D#": 38.890872965260115, 
    "Eb": 38.890872965260115, 
    "E": 41.20344461410874, 
    "F": 43.653528929125486, 
    "F#": 46.2493028389543, 
    "Gb": 46.2493028389543, 
    "G": 48.99942949771866,
    "G#": 51.91308719749314, 
}

valid_octaves = [0, 1, 2, 3, 4, 5, 6, 7, 8]


def times(t, hz=None):
    """Returns time sample values

    Returns an np.ndarray of time values representing points taken for ``t`` seconds, at samplerate ``hz``.

    The length of the resulting object is ``t * hz``

    Parameters
    ----------
    t : float, int, np.ndarray, chaudio.source.Source
        If float or int, it represents the number of seconds to generate time sample values for. If a numpy ndarray, it assumes the number of seconds is ``len(t)/hz``. If it is a chaudio.source.Source, it gets the number of seconds and sample rate (if ``hz`` is ``None``), and uses those.

    hz : float, int
        The sample rate (samples per second)

    Returns
    -------
    np.ndarray
        An array of time sample values, taken at ``hz`` samples per second, and lasting ``t`` (or value derived from ``t``) seconds.

    """
    
    _t = None
    if hz is None:
        if issubclass(type(t), chaudio.source.Source):
            hz = t.hz
        elif type(t) is np.ndarray:
            hz = chaudio.defaults["hz"]
        else:
            hz = chaudio.defaults["hz"]

    if _t is None:
        if issubclass(type(t), chaudio.source.Source):
            _t = t.seconds
        elif type(t) is np.ndarray:
            _t = len(t) / hz
        else:
            _t = t

    return np.arange(0, _t, 1.0 / hz)


def transpose(hz, cents):
    """Transposes a frequency value by a number of `cents <https://en.wikipedia.org/wiki/Cent_(music)>`_

    Note that if both ``hz`` and ``cents`` are np arrays, their shapes must be equivalent.

    The effects are thus: +1200 cents results in a shift up one octave, -1200 is a shift down one octave.


    Parameters
    ----------
    hz : float, int, np.ndarray
        Frequency, in oscillations per second

    cents : float, int, np.ndarray
        The number of cents to transpose ``hz``. It can be positive or negative.

    Returns
    -------
    float
        Frequency, in hz, of ``hz`` shifted by ``cents``

    """
    return hz * 2.0 ** (cents / 1200.0)


def note(name):
    """Frequency (in hz) of the note as indicated by ``name``

    ``name`` should begin with a note name (like ``A``, ``B``, ``C``, ... , ``G``), then optionally a ``#`` or ``b`` reflecting a sharp or flat (respectively) tone, and finally an optional octave number (starting with ``0`` up to ``8``).

    If no octave number is given, it defaults to ``4``.

    Parameters
    ----------
    name : str
        String representation of a note, like ``A`` or ``C#5``

    Returns
    -------
    float
        Frequency, in hz, of the note described by ``name``

    Examples
    --------

    >>> chaudio.note("A")
    440.0
    >>> chaudio.note("A5")
    880.0
    >>> chaudio.note("A#5")
    932.327523
    >>> chaudio.note("TESTING7")
    ValueError: invalid note name: TESTING

    """

    note_name = ""
    for i in name:
        if not i.isdigit():
            note_name += i
        else:
            break

    octave_number = name.replace(note_name, "")

    if octave_number == "":
        octave_number = 4
    else:
        octave_number = int(octave_number)

    if note_name not in valid_note_names.keys():
        raise ValueError("invalid note name: %s" % (note_name))

    if octave_number not in valid_octaves:
        raise ValueError("invalid octave number: %s" % (octave_number))

    return valid_note_names[note_name] * (2.0 ** octave_number)
    


def ensure_lr_dict(val):
    """Ensures the input is returned as a dictionary object with right and left specifiers

    If ``val`` is a dictionary, look for ``left`` or ``right`` keys. If both exist, return those as a new dictionary. If only one exists, assume that value stands for both sides.

    If ``val`` is a tuple/list, and it has 1 value, assume that is for both left and right. If it has length of 2, assum ``val[0]`` is the left value and ``val[1]`` is right.

    Else, assume the single ``val`` is the value for left and right, i.e. there is no difference between the two sides.

    If ``val`` does not fit these rules, a ``ValueException`` is raised.

    Parameters
    ----------
    val : any
        value to be ensured as a left/right dictionary

    Returns
    -------
    dict
        Value with keys 'left' and 'right', determined by the input value


    """
    if isinstance(val, dict):
        if "left" in val and "right" in val:
            return { "left": val["left"], "right": val["right"] }
        elif "left" in val:
            return { "left": val["left"], "right": val["left"] }
        elif "right" in val:
            return { "left": val["right"], "right": val["right"] }
        else:
            raise ValueError("Input dictionary has neither 'left' or 'right' value")
    elif isinstance(val, tuple) or isinstance(val, list):
        if len(val) == 0:
            raise ValueError("Input tuple/list has no items (length is 0")
        elif len(val) == 1:
            return { "left": val[0], "right": val[0] }
        elif len(val) == 2:
            return { "left": val[0], "right": val[1] }
        else:
            raise ValueError("Length of input is too large (> 2)")
    else:
        return { "right": val, "left": val }



# returns smallest normalization factor, such that -1.0<=v/normalize_factor(v)<=1.0, for all values in the array
def normalize_factor(v):
    """The factor needed to scale ``v`` in order to normalize to [-1.0, +1.0] range

    In the case that ``v`` is a chaudio.source.Source, return the highest of any sample in any channel.

    Parameters
    ----------
    v : chaudio.source.Source or np.ndarray
        The collection of amplitudes

    Returns
    -------
    float
        The highest maximum amplitude of the absolute value of ``v``

    """

    res = None
    if issubclass(type(v), chaudio.source.Source):
        res = max([normalize_factor(i) for i in v.data])
    elif type(v) is np.ndarray:
        res = np.max(np.abs(v))
    else:
        raise Exception("don't know how to normalize '%s'" % type(v).__name__)

    if res == 0:
        return 1.0
    else:
        return res

def normalize(v):
    """Return a scaled version of ``v`` in the [-1.0, +1.0] range

    Normalize ``v`` such that all values are scaled by the same linear factor, and :math:`-1.0 <= k <= +1.0` for all values ``k`` in ``v``. If given a chaudio.source.Source, all channels are scaled by the same factor (so that the channels will still be even).

    Parameters
    ----------
    v : chaudio.source.Source or np.ndarray
        The source being normalized

    Returns
    -------
    chaudio.source.Source or np.ndarray
        ``v`` such that all amplitudes have been scaled to fit inside the [-1.0, +1.0] range

    """

    return v / normalize_factor(v)


class TimeSignature:
    """

    Represents a `time signature <https://en.wikipedia.org/wiki/Time_signature>`_.

    """

    def __init__(self, beats, division, bpm=60):
        """TimeSignature creation routine

        Return a time signature representing measures each with ``beats`` beats (or pulses).

        The note represented as ``division`` getting a single beat.

        If division is 4, the quarter note gets the beat, 8 means the 8th note gets the beat, and so on.

        Parameters
        ----------
        v : chaudio.source.Source or np.ndarray
            The source being normalized

        beats : int, float
            Number of beats (or pulses) per measure
        
        division : int, float
            Note division that represents a single pulse

        bpm : int, optional
            The speed, in beats per minute

        """

        self.bpm = bpm
        self.beats = beats
        self.division = division


    def __getitem__(self, key):
        """Returns the time in seconds of a number of beats, or a number of measures and beats.

        (this method is an alias for subscripting, so ``tsig.__getitem__(key)`` is equivelant to ``tsig[key]``)

        If ``key`` is a tuple, return the number of seconds that is equivalant to ``key[0]`` measures, and ``key[1]`` beats.

        In all cases, ``tsig[a] == tsig[a//tsig.beats, a%tsig.beats]``.

        When calling using a ``key`` that is a tuple, ``key[1]`` must not exceed the number of beats. This is to prevent errors arising from improper lengths. However, the number of beats can be any non-negative value if using a key that is a float or int.

        Parameters
        ----------
        key : int, float, tuple
            Either a tuple containing (measure, beat), or a number of beats

        Returns
        -------
        float
            The amount of time that ``key`` represents (in seconds)

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
    

    def __str__(self):
        return "%d/%d" % (self.beats, self.division)

    __repr__ = __str__



