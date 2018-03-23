"""Utility Functions (:mod:`chaudio.util`)
=======================================


.. currentmodule:: chaudio.util

This module provides useful utilities and classes to be used elsewhere. Note that most of these functions are aliased directly to the main :mod:`chaudio` module. Ones that are not aliased are often lower level and may not support all input types.


"""

import numpy as np

import subprocess
import tempfile

import math

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

def concatenate(data):
    res = chaudio.Source(data[0])
    for i in data[1:]:
        res.append(i)
    return res

def sumdup(key, val):
    """ sums duplicates


    """
    dups, ind, counts = np.unique(key, return_index=True, return_counts=True)
    dup_val = val[ind]
    for dup in dups[counts>1]: 
        dup_val[np.where(dups==dup)] = np.sum(val[np.where(key==dup)])
    return dups, dup_val

def map_domain(domain, chunk, conversion_lambda):
    # this is used for transforming pitch
    # conversion_lambda is like lambda x: x * 2
    # and that will map each element of (domain[0], domain[1]) to (2 * domain[0], domain[1])
    # data is (frequency domain, amplitude)

    # in hz, bin size
    index_diff = domain[-1]-domain[-2]

    # the transformed domain
    domain_map = conversion_lambda(np.array(domain))

    selector_valid = (domain >= 0) & (domain_map >= 0) & (domain_map <= np.max(domain))

    res = []

    round_offset = 0

    output_bins = domain_map[selector_valid]
    output_selector = (output_bins / index_diff + round_offset).astype(np.int)

    for amps in chunk:
        c_out = np.zeros(len(amps), dtype=np.complex)

        combo_bins = sumdup(output_selector, np.array(amps)[selector_valid])

        #c_out[domain <= 0] = 0
        c_out[combo_bins[0]] = combo_bins[1]
        #c_out[output_selector] = sumdup(c_out[output_selector], np.array(amps)[selector_valid])[1]

        res.append(c_out)

    return res

def lambda_mask(data, qualifier):
    bool_mask = qualifier(data)
    return bool_mask * data


def fft_phase(fft_domain):
    return np.arctan2(fft_domain)

class Chunker(object):
    def __init__(self, audio, n=256, hop=None):
        self.audio = chaudio.Source(audio)
        self.n = n
        if hop is None:
            self.hop = n
        else:
            self.hop = hop

    def chunk_time(self):
        return float(self.hop) / self.audio.hz

    def chunk_time_offset(self, n):
        return float(n * self.n) / self.audio.hz

    def recombo(self, chunks):
        res = chaudio.util.concatenate([chunk for chunk in chunks])
        for i in range(0, res.channels):
            res[i] = res[i][:self.audio.samples]
        return res

    def chunks(self):
        for i in range(0, len(self)):
            yield self.chunk(i)

    def chunk(self, i):
        # returns time, data
        if self.hop * i + self.n > len(self.audio[0]):
            chunk = []
            for j in self.audio[:]:
                tchunk = j[self.hop * i:]
                chunk.append(np.append(tchunk, np.zeros(self.n - len(tchunk))))
        else:
            chunk = []
            for j in self.audio[:]:
                chunk.append(j[self.hop * i:self.hop * i + self.n])
        return chunk

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.chunk(key)
        elif isinstance(key, slice):
            return list(self.chunks())[key]
        else:
            raise KeyError("Unknown type for FFTChunker")

    def __len__(self):
        r = 0
        while self.hop * r + self.n <= self.audio.samples:
            r += 1
        return r + (self.audio.samples % self.hop != 0)



class FFTChunker(Chunker):

    def fft_map_domain(self, chunks, func):
        domain = self.domain()
        res = []
        for t, chunk in chunks:
            res.append(chaudio.util.map_domain(t, domain, chunk, func))
        return res

    def domain(self):
        return self.audio.hz * np.fft.rfftfreq(self.n)

    def fft_chunks(self, chunks):
        for chunk in chunks:
            yield self.fft_chunk(chunk)
    
    def ifft_chunks(self, chunks):
        for chunk in chunks:
            yield self.ifft_chunk(chunk)

    def fft_chunk(self, chunk):
        # returns t, list of channel tuples with (freq domain, values)
        return [np.fft.rfft(channel, n=self.n) for channel in chunk]

    def ifft_chunk(self, chunk):
        return [np.fft.irfft(channel, n=self.n) for channel in chunk]



def transpose(hz, val, use_cents=True):
    """Transposes a frequency value by a number of `cents <https://en.wikipedia.org/wiki/Cent_(music)>`_ or `semitones <https://en.wikipedia.org/wiki/Semitone>`_

    Note that if both ``hz`` and ``val`` are np arrays, their shapes must be equivalent.


    When, ``use_cents==True`` The effects are thus: +1200 val results in a shift up one octave, -1200 is a shift down one octave.

    When, ``use_cents==False`` The effects are thus: +12 val results in a shift up one octave, -12 is a shift down one octave.



    Parameters
    ----------
    hz : float, int, np.ndarray
        Frequency, in oscillations per second

    val : float, int, np.ndarray
        The number of cents (or semitones if ``use_cents==False``) to transpose ``hz``. It can be positive or negative.

    use_cents=True : bool
        Whether or not use use cents or semitones

    Returns
    -------
    float
        Frequency, in hz, of ``hz`` shifted by ``val``

    """
    if use_cents:
        return hz * 2.0 ** (val / 1200.0)
    else:
        return hz * 2.0 ** (val / 12.0)


def cents(hz):
    """Returns the number of cents (off of 1hz)

    Parameters
    ----------
    hz : float, int, np.ndarray
        Frequency, in oscillations per second

    Returns
    -------
    float, np.ndarray
        Cents off of 1 hz

    """
    return 1200 * np.log(hz) / np.log(2)

def hz(cents):
    return transpose(1, cents)

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
    if isinstance(note, float) or isinstance(note, int):
        return note

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

        return 60.0 * float(self.beats * measure + beat) / self.bpm
    

    def copy(self):
        return type(self)(self.beats, self.division, self.bpm)

    def __str__(self):
        return "%d/%d @%dbpm" % (self.beats, self.division, self.bpm)

    __repr__ = __str__


def glissando_freq(sfreq, efreq, t, discrete=False):
    """Returns an array of frequencies of a glissando starting at sfreq and ending at efreq

    Parameters
    ----------
    sfreq : float
        Frequency at the start of the time array

    efreq : float
        Frequency at the end of the time array
    
    t : np.ndarray
        Array of time sample values

    discrete : bool
        Default=False, but if true, they are truncated to note values

    Returns
    -------
    np.ndarray
        Array of frequencies in corresponding to `t`

    """

    if isinstance(sfreq, str):
        sfreq = note(sfreq)

    if isinstance(efreq, str):
        efreq = note(efreq)

    """

    math: exponential scaling, connect (st, sfreq) and (et, efreq) on the graph of y = base^(t-t[0]) * sfreq (where B is determined)

    """

    st = t[0]
    et = t[-1]

    tt = et - st

    base = (efreq / sfreq) ** (1.0 / tt)

    #steps = 12 * ((t - st) * np.log(base) + np.log(sfreq)) / np.log(2)
    steps = 12 * ((t - st) * (np.log(efreq / sfreq)) / tt+ np.log(sfreq) - np.log(440)) / np.log(2)

    if discrete:
        steps = steps - (steps % 1)
    
    steps += 12 * np.log(440) / np.log(2)

    freqs = hz(100 * steps)

    return freqs


def pair_video(output, video, audio, ffmpeg_bin="ffmpeg"):
    """

    Pairs an audio object with a video file

    The audio object should be chaudio object, video should be a string path

    """

    my_audio_out = None

    if isinstance(audio, str):
        my_audio_out = audio
    else:
        my_audio_out = tempfile.mkstemp(suffix=".wav")[1]
        chaudio.tofile(my_audio_out, audio)

    cmd = [
        ffmpeg_bin, "-y"
        "-i", video,
        "-i", my_audio_out,
        "-c:v", "copy", 
        "-c:a", "aac", 
        "-strict", "experimental", 
        output
    ]

    r = subprocess.call(cmd)
    if r != 0:
        chaudio.msgprint("error return code: " + str(r))




