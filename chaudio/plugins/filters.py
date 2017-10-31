"""

filters may reduce noise, re-equalize frequencies, remove frequencies, etc

"""

import scipy.signal

import chaudio
from chaudio.source import Source
from chaudio.util import times
from chaudio.plugins import Basic
from chaudio.waves import noise

# based on the Butterworth filter (https://en.wikipedia.org/wiki/Butterworth_filter), the actuation function based on frequency is nearly linear (in respect to gain in dB), so there not many artifacts around the pass zone
class Butter(Basic):
    # returns the coeficients for a normal filter operation
    def coef(self, cutoff, hz, order, btype):
        nyq = hz / 2.0
        normal_cutoff = cutoff / nyq
        # return butterworth design coefs
        b, a = scipy.signal.butter(order, normal_cutoff, btype=btype, analog=False)
        return b, a

    def process(self, _data):
        data = Source(_data)

        # 5 is good default
        order = self.getarg("order", 5)
        cutoff = self.getarg("cutoff", 30)
        hz = self.getarg("hz", chaudio.defaults["hz"])
        btype = self.getarg("btype", "highpass")

        b, a = self.coef(cutoff, hz, order, btype)

        # apply to all channels
        for i in range(0, data.channels):
            # TODO: implement some sort of master filter that hooks filter design coefficients (Butterworth) to filter (like filtfilt)
            data[i] = scipy.signal.filtfilt(b, a, data[i])

        return data
        
        