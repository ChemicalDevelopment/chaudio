"""

pitch shifts

"""

from chaudio.util import FFTChunker, transpose
from chaudio.plugins import Basic
import numpy as np
import scipy

import chaudio

class Stretch(Basic):
    def process(self, _data):
        """

        Kwargs
        ------

        """
        factor = self.getarg("factor", 1)

        data = chaudio.Source(_data)
        res = chaudio.Source(_data)

        for i in range(0, data.channels):
            # numpy interp method
            _xidx = np.arange(len(data[i]))
            _nxidx = np.arange(0, len(data[i]), 1.0 / factor)
            res[i] = np.interp(_nxidx, _xidx, data[i])

            # scipy resample method
            #res[i] = scipy.signal.resample(data[i], int(len(data[i]) * factor))


        return res

