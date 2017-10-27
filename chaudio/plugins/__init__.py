"""

audio plugins, for creating effects and managing pipelines

"""

import chaudio
from chaudio import waves

import numpy as np
import scipy
import scipy.signal as signal



# does nothing to audio, only stores it and retreives it, with hash to tell if it changed
class Basic(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __hash__(self):
        return hash(frozenset(self.kwargs.items()))

    def __str__(self):
        return "%s kwargs=%s" % (type(self).__name__, self.kwargs)

    __repr__ = __str__

    # the main method, this is called to actually perform on an object
    def process(self, _data):
        return _data

    # returns kwarg passed, or default if the dictionary does not contain it
    def getarg(self, key, default=None):
        if key in self.kwargs:
            return self.kwargs[key]
        else:
            return default

    # sets the kwargs[key] to val
    # if kwargs contains key already, will only replace it if replace=True
    def setarg(self, key, val, replace=True):
        if replace or key not in self.kwargs:
            self.kwargs[key] = val


# fades in and out
class Fade(Basic):
    def process(self, _data):
        data = chaudio.source.Source(_data)
        fadein = self.getarg("fadein", True)
        fadeout = self.getarg("fadeout", True)
        samples = self.getarg("samples", min([len(data)/8, data.hz * .04]))

        if not fadein and not fadeout:
            return data

        for i in range(0, int(samples)):
            if fadein:
                data[:,i] = np.array([j * float(i) / samples for j in data[:, i]])
            if fadeout:
                data[:,len(data) - i - 1] = np.array([j * float(i) / samples for j in data[:, len(data) - i - 1]])

        return data


# adds white noise to the input
class Volume(Basic):
    def process(self, _data):
        return self.getarg("amp", 1.0) * chaudio.Source(_data)


# adds white noise to the input
class Noise(Basic):
    def process(self, _data):
        data = chaudio.Source(_data)
        return data + self.getarg("amp", 1.0) * waves.noise(chaudio.times(data), -1)


# echos the input (not the same as reverb)
class Echo(Basic):
    def process(self, _data):
        data = chaudio.Source(_data)

        # delay, in samples
        delay = int(self.getarg("delay", 0))
        # initial delay, in samples
        idelay = int(self.getarg("idelay", 0))
        # how many repeats should we calculate
        num = self.getarg("num", 16)
        # amplitude of all echos
        amp = self.getarg("amp", .52)
        # decay of each iteration (multiplicative)
        decay = self.getarg("decay", .56)

        # used to pad data with zeros
        ipad = np.zeros((idelay,))
        pad = np.zeros((delay,))

        # start with zeros
        res = chaudio.Source(np.zeros((idelay + delay * num + len(data),)))

        # start with data, adding on room on the end for subsequent echos
        res += data.appended(np.repeat(pad, num)).appended(ipad)

        # add echos, essentially: add `num` delays with each successive one being `delay` frames farther from the start, it's volume multiplied by `decay`. These are all summed and multiplied by `amp`, then added to the original signal
        for i in range(1, num+1):
            res += (amp * (decay ** (i-1)) * data).prepended(ipad).prepended(np.repeat(pad, i)).appended(np.repeat(pad, num - i))

        return res

# similar to bit depth changing. Has the graphical effect of reducing resolution of the air pressure graph
class Pixelate(Basic):
    def process(self, _data):
        data = chaudio.Source(_data)

        # round each value to the nearest multiple of "step"
        step = self.getarg("step", chaudio.maxabs(data) / 15)

        if step <= 0:
            return data
        else:
            return data - (data % step)


class ButterFilter(Basic):
    def coef_pass(self, cutoff, hz, order, btype):
        nyq = hz / 2.0
        normal_cutoff = cutoff / nyq
        b, a = scipy.signal.butter(order, normal_cutoff, btype=btype, analog=False)
        return b, a

    def process(self, _data):
        data = chaudio.Source(_data)
        # 5 is good default
        order = self.getarg("order", 5)
        cutoff = self.getarg("cutoff", 30)
        hz = self.getarg("hz", 44100)
        btype = self.getarg("btype", "highpass")

        b, a = self.coef_pass(cutoff, hz, order, btype)
        
        for i in range(0, data.channels):
            data[i] = scipy.signal.filtfilt(b, a, data[i])

        return data
        