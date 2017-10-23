"""

audio plugins, for creating cool effects

"""

import chaudio
import numpy as np
import waveforms


# does nothing to audio, only stores it and retreives it, with hash to tell if it changed
class Basic:
    def __init__(self, start_data=None, **kwargs):
        self.kwargs = kwargs

        self.plugin_init()

        if start_data is not None:
            self.process(start_data)
        else:
            self.last_data = np.zeros((0, ), dtype=np.float32)

    def __hash__(self):
        return hash(type(self).__name__) + hash(frozenset(self.kwargs.items())) + hash(np.sum(self.last_data))

    def __str__(self):
        return "%s kwargs=%s" % (type(self).__name__, self.kwargs)

    def __repr__(self):
        return self.__str__()

    def _plugin_init(self):
        pass

    def _process(self, _data):
        return _data

    def plugin_init(self):
        return self._plugin_init()

    def process(self, _data):
        res = self._process(_data)
        self.last_data = np.copy(res)
        return res

    def get(self):
        return self.last_data

    # returns kwarg passed, or default if none is there
    def getarg(self, key, default=None):
        if key in self.kwargs:
            return self.kwargs[key]
        else:
            return default

    # acts as a numpy array with the last processed data
    def __getitem__(self, key):
        return self.last_data[key]

    # acts as a numpy array with the last processed data
    def __setitem__(self, key, val):
        self.last_data[key] = val

    # acts as a numpy array with the last processed data
    def __len__(self):
        return len(self.last_data)


# fades in and out
class Fade(Basic):
    def _plugin_init(self):
        pass

    def _process(self, _data):
        data = _data[:]
        fadein = self.getarg("fadein", True)
        fadeout = self.getarg("fadeout", True)
        samples = self.getarg("samples", None)

        if not fadein and not fadeout:
            return data

        if samples is None:
            samples = min([len(data)/8, 44100 * .04])

        for i in range(0, int(samples)):
            if fadein:
                data[i] *= float(i) / samples
            if fadeout:
                data[len(data) - i - 1] *= float(i) / samples

        return data


# adds white noise to the input
class Noise(Basic):
    def _plugin_init(self):
        pass

    def _process(self, _data):
        data = _data[:]
        return data + self.getarg("amp", 1.0) * waveforms.noise(chaudio.times(data), -1)


# echos the input (not the same as reverb)
class Echo(Basic):
    def _plugin_init(self):
        pass

    def _process(self, _data):
        # delay, in samples
        delay = int(self.getarg("delay", 0))

        # how many repeats should we calculate
        num = self.getarg("num", 16)
        
        # amplitude of all echos
        amp = self.getarg("amp", .52)
        
        # decay of each iteration (multiplicative)
        decay = self.getarg("decay", .56)


        # used to pad data with zeros
        pad = np.zeros((delay,), dtype=np.float32)

        # get np array
        data = _data[:]

        # start with zeros
        res = np.zeros((delay * num + len(data),), np.float32)

        # start with data, adding on room on the end for subsequent echos
        res += np.append(data, np.repeat(pad, num))

        # add echos, essentially: add `num` delays with each successive one being `delay` frames farther from the start, it's volume multiplied by `decay`. These are all summed and multiplied by `amp`, then added to the original signal
        for i in range(1, num+1):
            res += np.append(np.append(np.repeat(pad, i), amp * (decay ** (i-1)) * data), np.repeat(pad, num - i))

        return res

# similar to bit depth changing. Has the graphical effect of reducing resolution of the air pressure graph
class Pixelate(Basic):
    def _plugin_init(self):
        pass

    def _process(self, _data):
        data = _data[:]

        # round each value to the nearest multiple of "step"
        step = self.getarg("step", chaudio.maxabs(data) / 15)
        if step <= 0:
            return data
        else:
            return data - (data % step)


