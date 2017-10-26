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
import scipy.signal


try:
    import matplotlib
    from chaudio import viewer
    #print ("found matplotlib")
except:
    viewer = None
    #print ("no matplotlib support, graphing and similar features are disabled")

defaults = {}

defaults["hz"] = 44100
defaults["dtype"] = np.float32

def getdefault(key):
    global defaults
    return defaults[key]

def setdefault(key, val):
    global defaults
    defaults[key] = val

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
note = util.raw.note
times = util.raw.times

#normalize = util.raw.normalize
#combine = util.combine
#flatten = util.interleave
flatten = util.flatten

fromfile = util.io.fromfile
tofile = util.io.tofile
fromdatastr = util.io.fromdatastr
todatastr = util.io.todatastr

# left right vals
class ChannelsClass:
    pass

channels = ChannelsClass()
channels.L = 0
channels.R = 1

# audio source class
class Source:
    def __init__(self, data, channels=None, hz=None, dtype=None, auto_rechannel=True, auto_resample=True, auto_redtype=True):
        self.auto_rechannel = auto_rechannel
        self.auto_resample = auto_resample
        self.auto_redtype = auto_redtype

        if dtype is None:
            if type(data) is type(self):
                self._dtype = data.dtype
            else:
                self._dtype = getdefault("dtype")

        if channels is None:
            if type(data) is type(self):
                self._channels = data.channels
            elif type(data) in (tuple, list):
                self._channels = len(data)
            else:
                self._channels = 1
        else:
            self._channels = channels

        if hz is None:
            if type(data) is type(self):
                self._hz = data.hz
            else:
                self._hz = getdefault("hz")
        else:
            self._hz = hz


        assert(self._hz > 0 and self._channels >= 1)
        
        self.data = [None] * self._channels

        if type(data) is type(self):
            self.data = data.copy_data()
        elif type(data) in (tuple, list):
            assert(len(data) == self._channels)

            for i in range(0, self._channels):
                self.data[i] = np.array(data[i], dtype=self.dtype)
        else:
            assert(len(data) % self._channels == 0)

            for i in range(0, self._channels):
                self.data[i] = data[i::self._channels]

    def get_hz(self):
        return self._hz

    def set_hz(self, val):
        assert(val > 0)
        if self._hz != val and self.auto_resample:
            old_data = self.copy_data()
            old_dtype = self.dtype
            for i in range(0, len(old_data)):
                self.data[i] = (scipy.signal.resample(old_data[i], int(len(old_data[i]) * val / self._hz))).astype(old_dtype)

        self._hz = val

    def get_channels(self):
        return self._channels

    def set_channels(self, val):
        assert(val >= 1 and val <= 2)
        if self._channels != val and self.auto_rechannel:
            old_data = self.copy_data()

            # we know self._channels is NOT val
            if val == 1:
                self.data = [(old_data[0] + old_data[1]) / 2.0]
            elif val == 2:
                self.data = [old_data[0], old_data[0]]

        self._channels = val

        assert(self._channels == len(self.data))


    def get_dtype(self):
        return self._dtype

    def set_dtype(self, val):
        assert(val in (np.float32, np.int16, np.int32, np.int8, np.float, np.int))
        if self._dtype != val and self.auto_redtype:
            renorm_val = 1.0
            old_data = self.copy_data()
            old_scale = chaudio.util.norm_factor(self.dtype)
            new_scale = chaudio.util.norm_factor(val)
            to_scale = float(new_scale / old_scale) 

            for i in range(0, len(old_data)):
                self.data[i] = (to_scale * old_data[i].astype(np.float32)).astype(val)

        self._dtype = val



    hz = property(get_hz, set_hz)
    channels = property(get_channels, set_channels)
    dtype = property(get_dtype, set_dtype)

    def copy_data(self):
        return [np.copy(i) for i in self.data]
    
    def copy(self):
        return type(self)(self.copy_data(), self.channels, self.hz)

    # returns format dictionary
    def formatdict(self):
        return { "channels": self.channels, "hz": self.hz, "dtype": self.dtype }

    # returns the Source with the set number of channels, hz, and dtype
    def reformat(self, channels=None, hz=None, dtype=None):
        if channels is None:
            channels = self.channels
        if hz is None:
            hz = self.hz
        if dtype is None:
            dtype = self.dtype
        
        self_copy = self.copy()

        # getters and setters reformat for us
        self_copy.channels = channels
        self_copy.hz = hz
        self_copy.dtype = dtype

        return self_copy

    # this returns a packed numpy array of the (possibly multichannel)
    def flatten(self):
        if self.channels == 2:
            assert(len(self.data[0]) == len(self.data[1]))

        data_copy = self.copy_data()
        res = np.empty((len(data_copy) * len(data_copy[0]), ), dtype=self.dtype)

        for i in range(0, self.channels):
            res[i::self.channels] = data_copy[i]
        
        return res

    def __hash__(self):
        res = hash(self.channels)
        for i in range(0, self.channels):
            res += hash(self.data[i].tobytes())
        return res

    def __str__(self):
        return "Source[%s] %s hz" % (self.channels, self.hz)

    def __len__(self):
        agreed_len = len(self.data[0])
        for i in range(0, self.channels):
            assert(agreed_len == len(self.data[i]))
        return agreed_len

    # you should use source[CHANNEL][vals] (where CHANNEL can be ':' for a list of datas)
    def __getitem__(self, key):
        return self.data.__getitem__(key)

    def __add__(self, _v):
        v = type(self)(_v).reformat(**self.formatdict())
        for i in range(0, self.channels):
            print (len(v.data[i]), len(self.data[i]))
            print (chaudio.util.raw.maxabs(v.data[i]), chaudio.util.raw.maxabs(self.data[i]))
            v.data[i] = v.data[i] + self.data[i]
        return v

    def __mul__(self, _v):
        if type(_v) in (type(self), ):
            v = type(self)(_v).reformat(**self.formatdict())
            for i in range(0, self.channels):
                v.data[i] = self.data[i] * v.data[i]
            return v
        else:
            v = self.copy()
            for i in range(0, self.channels):
                v.data[i] = self.data[i] * _v
            return v

    def __truediv__(self, _v):
        if type(_v) in (type(self), ):
            v = type(self)(_v).reformat(**self.formatdict())
            for i in range(0, self.channels):
                v.data[i] = self.data[i] / v.data[i]
            return v
        else:
            v = self.copy()
            for i in range(0, self.channels):
                v.data[i] = self.data[i] / _v
            return v


        

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

