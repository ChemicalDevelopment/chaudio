"""

chaudio: programmatic music synthesis

github.com/chemicaldevelopment/chaudio

ChemicalDevelopment 2017

Authors:
  - Cade Brown


"""

# system imports
import wave

import chaudio

# other chaudio classes
from chaudio import util

from chaudio import waveforms
from chaudio import plugins
from chaudio import arrangers

# libraries
import numpy as np
import scipy as sp

try:
    import matplotlib
    from chaudio import viewer
    print ("found matplotlib")
except:
    viewer = None
    print ("no matplotlib support, graphing and similar features are disabled")


# alias functions to the module name
# to see documentation, see util.py
note = util.note
combine = util.combine
times = util.times
normalize = util.normalize
fromfile = util.fromfile
tofile = util.tofile
flatten = util.flatten

# time signature class, for use with ExtendedArranger and others
class TimeSignature:
    # default is 4/4
    def __init__(self, top=4, bottom=4, bpm=80):
        self.bpm = bpm
        self.top = top
        self.bottom = bottom


    # time[a, b] returns the time (in seconds) of the b'th beat of the a'th measure
    def __getitem__(self, key):
        if type(key) != tuple:
            raise KeyError("TimeSignature key should be tuple (timesig[a,b])")

        measure, beat = key

        if beat >= self.top:
            raise ValueError("beat for time signature should be less than top value (err %s >= %s)" % (beat, self.top))

        return 60.0 * (self.top * measure + beat) / self.bpm
    
    # so you can print out time signatures
    def __str__(self):
        return "%d/%d" % (self.top, self.bottom)

    def __repr__(self):
        return self.__str__()

