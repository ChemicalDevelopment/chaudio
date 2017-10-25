"""

chaudio: programmatic music synthesis

github.com/chemicaldevelopment/chaudio

ChemicalDevelopment 2017

Authors:
  - Cade Brown


"""


from __future__ import print_function


# system imports
import wave
import glob
import os 
import sys
import ntpath

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
    #print ("found matplotlib")
except:
    viewer = None
    #print ("no matplotlib support, graphing and similar features are disabled")

# normal print, which uses stderr so pipes still work
def msgprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# prints to stdout and can be piped
def dataprint(data, *args, **kwargs):
    sys.stdout.write(util.todatastr(data[:], *args, **kwargs))


chaudio_dir = os.path.dirname(os.path.realpath(__file__))
samples_dir = os.path.join(chaudio_dir, "samples")

if os.path.isdir(samples_dir):
    _samples = glob.glob(samples_dir + "/*.wav")
    samples = {}
    for i in _samples:
        samples[ntpath.basename(i)] = i
else:
    chaudio.msgprint("warning: samples directory not found")


# alias functions to the module name
# to see documentation, see util.py
note = util.note
times = util.times

normalize = util.normalize
combine = util.combine
flatten = util.interleave
flatten = util.flatten

fromfile = util.fromfile
tofile = util.tofile
fromdatastr = util.fromdatastr
todatastr = util.todatastr

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

