"""

Returns just the top (the opposite of a clipper)

"""

import chaudio
import numpy as np
from chaudio.source import Source
from chaudio.plugins import Basic

class TopCropper(Basic):
    """

    Returns what would be clipped off

    """    
    def process(self, _data):
        """Returns the top part of the wave

        Kwargs
        ------

        :"cutoff": where to slice the return

        :"relative": if true, then take 'cutoff' as a ratio (from 0.0 to 1.0) of the percentage of the graph, otherwise the actual value

        """

        data = Source(_data)

        cutoff = self.getarg("cutoff", .82)
        relative = self.getarg("cutoff", True)

        xf = chaudio.util.normalize_factor(data)

        r_channels = []

        for i in range(0, data.channels):
            rd = data[i]
            if relative:
                rd = rd / xf
            rd[np.where((rd >= 0) & (rd < cutoff))] = cutoff
            rd[np.where((rd < 0) & (rd > -cutoff))] = -cutoff
            rd[np.where(rd > 0)] -= cutoff
            rd[np.where(rd < 0)] += cutoff
            if relative:
                rd = rd * xf
            r_channels += [ rd ]

        return Source(r_channels)

