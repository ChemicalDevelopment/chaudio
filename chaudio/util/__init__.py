"""

utilities

"""

import chaudio

import chaudio.util.raw
import chaudio.util.freq





# time signature class, for use with ExtendedArranger and others
class TimeSignature:
    # default is 4/4
    def __init__(self, top=4, bottom=4, bpm=80):
        self.bpm = bpm
        self.top = top
        self.bottom = bottom


    # time[a, b] returns the time (in seconds) of the b'th beat of the a'th measure
    def __getitem__(self, key):
        if type(key) != tuple:
            raise KeyError("TimeSignature key should be tuple (timesig[a,b])")

        measure, beat = key

        if beat >= self.top:
            raise ValueError("beat for time signature should be less than top value (err %s >= %s)" % (beat, self.top))

        return 60.0 * (self.top * measure + beat) / self.bpm
    
    # so you can print out time signatures
    def __str__(self):
        return "%d/%d" % (self.top, self.bottom)

    def __repr__(self):
        return self.__str__()






