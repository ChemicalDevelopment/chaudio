"""

utilities

"""

import numpy as np

import chaudio
import chaudio.util.freq


# returns array of sample times
# if a time (in seconds) is returned, the default hz value from chaudio.defaults is taken if hz==None
# if it's a source, we get how many seconds it lasts, and duplicate an array that would fit it
def times(v, hz=None):
    t = None
    if hz is None:
        if issubclass(type(v), chaudio.source.Source):
            hz = v.hz
            t = v.seconds
        elif type(v) is np.ndarray:
            hz = chaudio.defaults["hz"]
            t = len(v) / hz
        else:
            hz = chaudio.defaults["hz"]

    if t is None:
        t = v

    return np.arange(0, t, 1.0 / hz)

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

# time signature class, for use with ExtendedArranger and others
class TimeSignature:
    # default is 4/4
    def __init__(self, beats=4, division=4, bpm=80):
        self.bpm = bpm
        self.beats = beats
        self.division = division

    # time[a, b] returns the time (in seconds) of the b'th beat of the a'th measure
    def __getitem__(self, key):
        if type(key) != tuple:
            raise KeyError("TimeSignature key should be tuple (timesig[a,b])")

        measure, beat = key

        if beat >= self.beats:
            raise ValueError("beat for time signature should be less than the number of beats in a measure (err %s >= %s)" % (beat, self.beats))

        return 60.0 * (self.beats * measure + beat) / self.bpm
    
    # so you can print out time signatures
    def __str__(self):
        return "%d/%d" % (self.beats, self.division)

    __repr__ = __str__





