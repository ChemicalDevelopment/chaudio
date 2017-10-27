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
    def __init__(self, start_data=None, **kwargs):
        self.kwargs = kwargs

        self.plugin_init()

    def __hash__(self):
        return hash(frozenset(self.kwargs.items()))

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
        return self._process(_data)

    # returns kwarg passed, or default if none is there
    def getarg(self, key, default=None):
        if key in self.kwargs:
            return self.kwargs[key]
        else:
            return default


# fades in and out
class Fade(Basic):
    def _plugin_init(self):
        pass

    def _process(self, _data):
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
    def _plugin_init(self):
        pass

    def _process(self, data):
        return self.getarg("amp", 1.0) * chaudio.Source(data)


# adds white noise to the input
class Noise(Basic):
    def _plugin_init(self):
        pass

    def _process(self, _data):
        data = chaudio.Source(_data)
        return data + self.getarg("amp", 1.0) * waves.noise(chaudio.times(data), -1)


# echos the input (not the same as reverb)
class Echo(Basic):
    def _plugin_init(self):
        pass

    def _process(self, _data):
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
    def _plugin_init(self):
        pass

    def _process(self, _data):
        data = chaudio.Source(_data)

        # round each value to the nearest multiple of "step"
        step = self.getarg("step", chaudio.maxabs(data) / 15)

        if step <= 0:
            return data
        else:
            return data - (data % step)


class ButterFilter(Basic):
    def _plugin_init(self):
        pass

    def coef_pass(self, cutoff, hz, order, btype):
        nyq = hz / 2.0
        normal_cutoff = cutoff / nyq
        b, a = scipy.signal.butter(order, normal_cutoff, btype=btype, analog=False)
        return b, a

    def _process(self, _data):
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
        
# shifts the pitch by so many cents
class PitchShift(Basic):
    def _plugin_init(self):
        pass

    def _process(self, _data):
        raise Exception("not implemented")
        data = chaudio.Source(_data)

        cents = self.getarg("cents", 0)
        hz = self.getarg("hz", 44100)

        N = hz // 21

        pad = np.zeros((N, ), dtype=np.float32)
        res = np.zeros((N * (1 + len(data)//N), ), dtype=np.float32)
        
        for i in range(0, len(data)//N + 1):
            this_slice = data[N * i:N * (i + 1)]
            if i >= len(data) // N:
                this_slice = np.append(this_slice, np.zeros((N * (i + 1) - len(data), )))
            fftdata = np.fft.rfft(this_slice)
            fftx = np.fft.rfftfreq(N) * hz
            
            fftinterval = (fftx[1] - fftx[0])

            pitch_ratio = 2.0 ** (cents / 1200.0)

            sfftdata = np.zeros(fftdata.shape, dtype=fftdata.dtype)

            bins_to_delete = None

            for j in range(0, len(fftdata)):
                cpitch = fftx[j]
                desired_pitch = cpitch * pitch_ratio
                desired_bin = int(desired_pitch / fftinterval)
                #print (i, desired_bin)
                
                if bins_to_delete is None:
                    bins_to_delete = desired_bin
                #print (i, desired_bin)
                if desired_bin < len(sfftdata):
                    #print ('nonzero')
                    sfftdata[desired_bin] = fftdata[j]
            
            #print (bins_to_delete)
            #sfftdata[:bins_to_delete] = 0
            #import viewer
            #viewer.show_raw(fftx, np.abs(fftdata))
            #viewer.show_raw(fftx, np.abs(sfftdata))
            #viewer.show()

            prepadded = np.append(np.repeat(pad, i), np.fft.irfft(sfftdata, N))
            appended_data = np.append(prepadded, np.repeat(pad, len(data)//N - i))
            res += np.real(appended_data)

        #bins_to_shift = cents / fftinterval

        #print (bins_to_shift)
        
        #print (sfftdata)



        return res






