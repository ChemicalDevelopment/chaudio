"""Programmatic Music Synthesis (:mod:`chaudio`)
====================================================

.. currentmodule:: chaudio

Submodules:


.. autosummary::
    :toctree: submodules

    arrangers
    instruments
    io
    plugins
    source
    util
    waves

"""


# compatability between python versions
from __future__ import (absolute_import, division, print_function, unicode_literals)

# system level inputs
import sys
import os
import glob
import ntpath

# other required libraries
import numpy as np
import scipy

# submodules for chaudio
import chaudio
import chaudio.source
import chaudio.arrangers
import chaudio.plugins
import chaudio.waves
import chaudio.instruments
import chaudio.util
import chaudio.io


# add useful aliases so frequently used functions/types are easy to access

# functions

times = chaudio.util.times
note = chaudio.util.note

tofile = chaudio.io.tofile
fromfile = chaudio.io.fromfile

play = chaudio.io.play

# classes

Source = chaudio.source.Source

TimeSignature = chaudio.util.TimeSignature


# normal print, which uses stderr so that we can pipe data between processes
def msgprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# prints to stdout, so that other processes in the PIPE can receive it
def dataprint(data, *args, **kwargs):
    sys.stdout.write(data, *args, **kwargs)



# defaults, for assuming input parameters, for example
defaults = {}

# 44100 hz is the most common sample rate
defaults["hz"] = 44100

# the internal data format should always be a floating point
defaults["dtype"] = np.float64

defaults["timesignature"] = TimeSignature(4, 4)


# actual module directory in the filesystem
chaudio_dir = os.path.dirname(os.path.realpath(__file__))
samples_dir = os.path.join(chaudio_dir, "samples")

# a class to get sample data without requiring every import of chaudio to read from these, which can be time consuming
class Samples:

    # sample_files is an array of sample file's locations on the filesystem
    def __init__(self, sample_files):
        self.fullpaths = {}
        for f in sample_files:
            # ntpath basename returns filename, removing any preceding directories
            self.fullpaths[ntpath.basename(f)] = f

    # they asked for sample data, so calculate and return it
    def __getitem__(self, key):
        return fromfile(self.fullpaths[key])
    
    # returns
    def __str__(self):
        return self.fullpaths.keys()

    __repr__ = __str__


#samples = None

# if the samples are found, create an object for people asking for samples
if os.path.isdir(samples_dir):
    samples = Samples(glob.glob(samples_dir + "/*.wav"))
else:
    chaudio.msgprint("warning: samples directory not found")

