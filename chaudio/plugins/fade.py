"""

fades in and out

"""

import numpy as np

from chaudio.source import Source
from chaudio.plugins import Basic

# fades in and out
class Fade(Basic):
    def process(self, _data):
        data = Source(_data)
        fadein = self.getarg("fadein", True)
        fadeout = self.getarg("fadeout", True)
        sec = self.getarg("sec", .05)
        samples = min([len(data)/2, int(sec * data.hz)])

        if not fadein and not fadeout:
            return data

        for i in range(0, data.channels):
            if fadein:
                data[i,:samples] *= np.linspace(0, 1, samples)
            if fadeout:
                data[i,-samples:] *= np.linspace(1, 0, samples)

        return data
