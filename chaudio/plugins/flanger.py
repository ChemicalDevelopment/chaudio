"""

Flanger

"""

import chaudio
import numpy as np
from chaudio.source import Source
from chaudio.plugins import Basic

class Flanger(Basic):
    """

    To do flanging: https://en.wikipedia.org/wiki/Flanging

    """    
    def process(self, _data):
        """Returns the result, but amplified

        Kwargs
        ------

        :"offset_lfo": a :class:`chaudio.instruments.lfo` to determine the offset


        """

        data = Source(_data)

        # amplitude and dc_shift are taken to be in milliseconds (as far as the flanger offset)
        offset_lfo = self.getarg("offset_lfo", chaudio.instruments.LFO(hz=1.2, amp=8.0, dc_shift=10.0))

        offset_samples = (data.hz * offset_lfo.calc_val(chaudio.times(data)) / 1000.0).astype(np.int32)
        
        abs_samples = np.arange(len(offset_samples)) + offset_samples
        abs_samples[np.where(abs_samples < 0)] = 0
        max_allowed_idx = min([len(c) for c in data[:]])
        abs_samples[np.where(abs_samples >= max_allowed_idx)] = max_allowed_idx - 1

        r_channels = []

        for i in range(0, data.channels):
            r_channels += [data[i] + data[i][abs_samples]]

        return Source(r_channels)

