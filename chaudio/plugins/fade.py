"""

A gentle fade in and out

"""

import numpy as np

from chaudio.source import Source
from chaudio.plugins import Basic

class Fade(Basic):

    """
    
    A gentle fade in and out


    """    

    def process(self, _data):
        """Returns the result, but faded given a few parameters

        Kwargs
        ------

        :"fadein": ``True`` to fade at the beginning, ``False`` to not
        :"fadeout": ``True`` to fade at the end, ``False`` to not
        :"sec": the length, in seconds, of how long to fade

        Essentially for the first samples til ``sec`` are scaled linearly if ``fadein``, and the last samples from ``t-sec`` til ``t`` are scaled linearly if ``fadeout`` is enabled.

        """

        data = Source(_data)
        fadein = self.getarg("fadein", True)
        fadeout = self.getarg("fadeout", True)
        sec = self.getarg("sec", .01)
        samples = min([int(len(data)/2), int(sec * data.hz)])

        if not fadein and not fadeout:
            return data

        for i in range(0, data.channels):
            if fadein:
                data[i][:samples] *= np.linspace(0, 1, samples)
            if fadeout:
                data[i][-samples:] *= np.linspace(1, 0, samples)

        return data
