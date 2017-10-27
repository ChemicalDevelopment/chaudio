
import sys
import os
import glob
import ntpath

import chaudio
import chaudio.source
import chaudio.arrangers
import chaudio.waves
import chaudio.util
import chaudio.io

import numpy as np


# add useful defaults
times = chaudio.util.raw.times
note = chaudio.util.freq.note

tofile = chaudio.io.tofile
fromfile = chaudio.io.fromfile

Source = chaudio.source.Source

TimeSignature = chaudio.util.TimeSignature



defaults = {}

defaults["hz"] = 44100
defaults["dtype"] = np.float64


# normal print, which uses stderr so pipes still work
def msgprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# prints to stdout and can be piped
def dataprint(data, *args, **kwargs):
    sys.stdout.write(util.todatastr(data[:], *args, **kwargs))

def getdefault(key):
    global defaults
    return defaults[key]

def setdefault(key, val):
    global defaults
    defaults[key] = val




chaudio_dir = os.path.dirname(os.path.realpath(__file__))
samples_dir = os.path.join(chaudio_dir, "samples")

if os.path.isdir(samples_dir):
    _samples = glob.glob(samples_dir + "/*.wav")
    samples = {}
    for i in _samples:
        samples[ntpath.basename(i)] = i
else:
    chaudio.msgprint("warning: samples directory not found")

