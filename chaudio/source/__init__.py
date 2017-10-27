"""

for audio sources

"""

import chaudio
import numpy as np

import scipy
import scipy.signal

class Source:
    def __init__(self, data, hz=None, dtype=None):
        if issubclass(type(data), Source):
            self._data = data.copy_data()
            self._channels = data.channels
        elif type(data) in (tuple, list):
            # assume mono input
            assert(len(data) >= 1)
            self._data = list(data)
        elif type(data) is np.ndarray:
            self._data = [data]
        elif issubclass(type(data), chaudio.arrangers.Arranger):
            self._data = data.source.copy_data()
            self._channels = data.source.channels
        else:
            raise Exception("Don't know how to convert '%s' into '%s'" % (type(data).__name__, type(self).__name__))

        if hz is None:
            if issubclass(type(data), Source):
                self._hz = data.hz
            else:
                self._hz = chaudio.getdefault("hz")
        else:
            self._hz = hz

        if dtype is None:
            if issubclass(type(data), Source):
                self._dtype = data.dtype
            elif type(data) is np.ndarray:
                self._dtype = data.dtype
            else:
                self._dtype = chaudio.getdefault("dtype")
        else:
            self._dtype = dtype
    
        self.dtype = self._dtype


    def copy_data(self):
        r = [None] * self.channels
        for i in range(0, self.channels):
            r[i] = np.copy(self.data[i])
        return r

    def copy(self):
        return type(self)(self.copy_data(), self.hz)

    def resample(self, tohz):
        r = self.copy()
        r.hz = tohz
        return r

    def rechannel(self, tochannels):
        r = self.copy()
        r.channels = tochannels
        return r

    def redtype(self, todtype):
        r = self.copy()
        r.dtype = todtype
        return r

    # getters and setters
    def get_data(self):
        return self._data
            
    def set_data(self, v):
        self._data = v
        # TODO ensure correctness

    def get_dtype(self):
        return self._dtype

    def set_dtype(self, v):
        for i in range(0, self.channels):
            self.data[i] = self.data[i].astype(v)
        self._dtype = v

    def get_channels(self):
        return len(self.data)

    def set_channels(self, v):
        # only these are supported
        assert(v in (1, 2))
        if v != self.channels:
            # we know that our channels is 1 if v = 2, and 2 if v = 1
            if v == 1:
                assert(len(self.data) == 2)
                self.data = [(self.data[0] + self.data[1]) / 2.0]
            else:
                assert(len(self.data) == 1)
                self.data = [self.data[0], self.data[0]]
    
    def get_hz(self):
        return self._hz

    def set_hz(self, v):
        # TODO resample
        if self.hz != v:
            for i in range(0, self.channels):
                self.data[i] = scipy.signal.resample(self.data[i], int(len(self.data[i]) * v / self._hz))
            
            self._hz = v

    def get_seconds(self):
        return self.samples / self.hz

    def set_seconds(self):
        raise Exception("seconds is not a settable property!")

    def get_samples(self):
        agree_len = len(self.data[0])
        for i in range(1, len(self.data)):
            if agree_len != len(self.data[i]):
                raise Exception("internal error: channels have different length")
        return agree_len

    def set_samples(self, v):
        raise Exception("samples is not a settable property!")


    data = property(get_data, set_data)
    dtype = property(get_dtype, set_dtype)
    channels = property(get_channels, set_channels)
    hz = property(get_hz, set_hz)
    seconds = property(get_seconds, set_seconds)
    samples = property(get_samples, set_samples)


    # overriding methods

    # string represnetation, showing channels, samples, and samplerate
    def __str__(self):
        return "Source[%s] %sl %.2fs %shz" % (self.channels, self.samples, self.seconds, self.hz)

    # returns sample length
    def __len__(self):
        return self.samples

    # use like source[channel:index] (channel can be : for all channels)
    # this returns either a numpy array or tuple/list of numpy arrays
    def __getitem__(self, key):
        assert(type(key) in (int, tuple, slice))
        if type(key) is tuple:
            # it has multiple keys, so return them on internal data
            assert(len(key) == 2)
            k0 = self.data[key[0]]
            if type(k0) is not list:
                k0 = [k0]
            return [i[key[1]] for i in k0]
        else:
            # they are asking for a specific channel
            return self.data[key]

    # use like source[channel:index] (channel can be : for all channels)
    # this returns either a numpy array or tuple/list of numpy arrays
    def __setitem__(self, key, val):
        assert(type(key) in (int, tuple, slice))
        if type(key) is tuple:
            if issubclass(type(val), Source):
                valc = val.copy()
                valc.channels = self.channels
                valc.hz = self.hz
                self.data[key[0]][key[1]] = valc
            elif type(val) in (int, float):
                # MAY BE ERROR HERE, check and make sure fade plugin is working
                for x in self.data[key[0]]:
                    x[key[1]] = val
            elif type(val) is np.ndarray:
                if type(key[0]) is int:
                    self.data[key[0]][key[1]] = val
                else:
                    for x in self.data[key[0]]:
                        x[key[1]] = val
            else:
                raise Exception("don't know how to set '%s'" % type(val))
        else:
            # they are asking for a specific channel
            self.data[key] = val

    def prepend(self, _v):
        v = Source(_v)
        v.hz = self.hz
        v.channels = self.channels
        for i in range(0, self.channels):
            self._data[i] = np.append(v.data[i], self._data[i])

    def append(self, _v):
        v = Source(_v)
        v.hz = self.hz
        v.channels = self.channels
        for i in range(0, self.channels):
            self._data[i] = np.append(self._data[i], v.data[i])

    # returns a copy
    def prepended(self, _v):
        r = self.copy()
        r.prepend(_v)
        return r

    # returns a copy
    def appended(self, _v):
        r = self.copy()
        r.append(_v)
        return r

    def ensure(self, length=None):
        if length is not None and length > len(self._data[0]):
            needed_len = length - len(self._data[0])
            pad = np.zeros((needed_len, ), dtype=self.dtype)
            for i in range(0, self.channels):
                self._data[i] = np.append(self._data[i], pad)

    # returns what to operate on channels with any operator
    def __opit__(self, v):
        if issubclass(type(v), Source):
            v.hz = self.hz
            v.channels = self.channels
            return v.data
        elif issubclass(type(v), chaudio.arrangers.Arranger):
            return self.__opit__(v.source)
        elif type(v) is np.ndarray:
            return [v] * self.channels
        else:
            r = [np.array([v] * self.samples, dtype=self.dtype)] * self.channels
            return r

    # all operators are distributed if float/int, or paired if arrays
    def __add__(self, _v):
        r = self.copy()
        v = self.__opit__(_v)
        for i in range(0, self.channels):
            r.data[i] += v[i]
        return r

    def __mul__(self, _v):
        r = self.copy()
        v = self.__opit__(_v)
        for i in range(0, self.channels):
            r.data[i] *= v[i]
        return r

    def __truediv__(self, _v):
        r = self.copy()
        v = self.__opit__(_v)
        for i in range(0, self.channels):
            r.data[i] /= v[i]
        return r

    def __floordiv__(self, _v):
        r = self.copy()
        v = self.__opit__(_v)
        for i in range(0, self.channels):
            r.data[i] //= v[i]
        return r

    __radd__ = __add__
    __rmul__ = __mul__


class Mono(Source):
    def __init__(self, data, hz=None):
        super().__init__(data, hz)
        self.channels = 1

    def set_channels(self, v):
        raise Exception("Can not set channels on a %s source!" % type(self).__name__)


class Stereo(Source):
    def __init__(self, data, hz=None):
        super().__init__(data, hz)
        self.channels = 2

    def set_channels(self, v):
        raise Exception("Can not set channels on a %s source!" % type(self).__name__)





