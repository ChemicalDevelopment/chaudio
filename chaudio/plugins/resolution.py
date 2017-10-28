"""

changes the minimum resolution

rounds each sample to the nearest value of "step", which has the graphical effect of a "pixelated" waveform (similar to square wave)

"""

import numpy as np

from chaudio.source import Source
from chaudio.plugins import Basic
from chaudio.util import normalize_factor

# similar to bit depth changing. Has the graphical effect of reducing resolution of the air pressure graph
class Resolution(Basic):
    def process(self, _data):
        data = Source(_data, dtype=np.float32)

        # do we first normalize the data, apply the filter, and then scale it back
        norm = self.getarg("norm", True)

        # our normalization factor
        factor = normalize_factor(data)

        # round each value to the nearest multiple of "step"
        step = self.getarg("step", .15)

        #if step <= 0:
        #    raise ValueError("step can not be <= 0 (value given was '%s')" % step)

        # normalize it so step is on a 0.0 to 1.0 step
        if norm:
            data = data / norm

        # this is done so we can handle division by zero
        with np.errstate(divide='ignore', invalid='ignore'):
            # essentially set it to the nearest multiple of step
            for i in range(0, data.channels):
                # original data
                odata = data[i]
                cdata = odata / step
                data[i] = np.fix(cdata) * step
                # any that were divided by zero, step size zero means exact precision, so set those to the original data
                data[i][~np.isfinite(cdata)] = odata[~np.isfinite(cdata)]

        # unnormalize it so it has roughly the same amplitudes
        if norm:
            data = data * norm

        return data

