"""

filters to remove frequency ranges, pass zones, bands, etc

"""

import scipy.signal

import chaudio
from chaudio.source import Source
from chaudio.util import times
from chaudio.plugins import Basic
from chaudio.waves import noise


class Butter(Basic):
    """
    
    Butterworth filter (https://en.wikipedia.org/wiki/Butterworth_filter), the actuation function based on frequency is nearly linear (in respect to gain in dB), so there not many artifacts around the pass zone

    """

    # returns the coeficients for a normal filter operation
    def coef(self, cutoff, hz, order, btype):
        """Internal function for getting the filter coefficients

        """

        nyq = hz / 2.0
        normal_cutoff = cutoff / nyq
        # return butterworth design coefs
        b, a = scipy.signal.butter(order, normal_cutoff, btype=btype, analog=False)
        return b, a

    def process(self, _data):
        """Return the result, with some frequencies filtered out

        Kwargs
        ------

        :"order": Butterworth filter order, which should probably stay at ``5`` (the default)
        :"cutoff": Frequency, in ``hz``, of the cutoff. If ``btype`` is ``highpass``, then anything above ``cutoff`` remains in the resulting signal (i.e. the high values pass). If ``btype=="lowpass"``, all frequencies lower than ``cutoff`` remain in the signal.
        :"btype": What filter type? Possible values are "highpass" and "lowpass".

        """

        data = Source(_data)

        # 5 is good default
        order = self.getarg("order", 5)
        cutoff = self.getarg("cutoff", 30)
        hz = data.hz
        btype = self.getarg("btype", "highpass")

        b, a = self.coef(cutoff, hz, order, btype)

        # apply to all channels
        for i in range(0, data.channels):
            # TODO: implement some sort of master filter that hooks filter design coefficients (Butterworth) to filter (like filtfilt)
            data[i] = scipy.signal.filtfilt(b, a, data[i])

        return data
        
        