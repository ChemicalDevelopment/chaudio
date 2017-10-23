"""

audio plugins, for creating cool effects

"""

import chaudio
import numpy as np
import waveforms


# does nothing to audio, only stores it
class BasicPlugin:
    def __init__(self, start_data=None, **kwargs):
        self.kwargs = kwargs

        self.plugin_init()

        if start_data is not None:
            self.process(start_data)
        else:
            self.last_data = np.zeros((0, ), dtype=np.float32)


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

    def __getitem__(self, key):
        return self.last_data[key]

    def __setitem__(self, key, val):
        self.last_data[key] = val

    def __len__(self):
        return len(self.last_data)


class SmoothPlugin(BasicPlugin):
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
            samples = min([len(data)/4, 44100 * .1])

        for i in range(0, int(samples)):
            if fadein:
                data[i] *= float(i) / samples
            if fadeout:
                data[len(data) - i - 1] *= float(i) / samples

        return data


class NoisePlugin(BasicPlugin):
    def _plugin_init(self):
        pass

    def _process(self, _data):
        data = _data[:]
        return data + self.getarg("amp", 1.0) * waveforms.noise(chaudio.times(data), -1)



class EchoPlugin(BasicPlugin):
    def _plugin_init(self):
        pass

    def _process(self, _data):
        delay = self.getarg("delay", 0)
        num = self.getarg("num", 16)
        amp = self.getarg("amp", .6)
        decay = self.getarg("decay", .56)
        pad = np.zeros((delay,), dtype=np.float32)

        data = _data[:]

        res = np.zeros((delay * num + len(data),), np.float32)
        res += np.append(data, np.repeat(pad, num))

        for i in range(1, num+1):
            res += np.append(np.append(np.repeat(pad, i), amp * (decay ** (i-1)) * data), np.repeat(pad, num - i))

        return res


class PixelatePlugin(BasicPlugin):
    def _plugin_init(self):
        pass

    def _process(self, _data):
        data = _data[:]
        step = self.getarg("step", chaudio.maxabs(data) / 15)
        if step <= 0:
            return data
        else:
            return data - (data % step)


