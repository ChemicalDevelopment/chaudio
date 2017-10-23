"""

general utilities


"""

# system imports
import wave
import struct
import math

# libraries
import numpy as np

# chaudio imports
import waveforms
import plugins
import arrangers

# returns an array of times
def times(ar, hz=44100):
    # if ar is just a time value (in seconds, return array based on that)
    if isinstance(ar, float) or isinstance(ar, int):
        return np.arange(0, ar, 1.0 / hz)
    # else, assume it is sample data and return resulting arange based on that
    elif type(ar) is np.ndarray:
        return times(float(len(ar)) / hz, hz)

# returns max of absolute value
def maxabs(data):
    return np.max(np.abs(data))

# returns a normalized audio between -1.0 and 1.0
def normalize(audio):
    # stereo input
    if isinstance(audio, tuple):
        to_div = max(maxabs(audio[0]), maxabs(audio[1]))
        return audio[0] / to_div, audio[1] / to_div
    else:
        return audio / maxabs(audio)

# time signature class, for use with ExtendedArranger and others
class TimeSignature:
    # default is 4/4
    def __init__(self, top=4, bottom=4, bpm=80):
        self.bpm = bpm
        self.top = 4
        self.bottom = 4

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


# returns audiodata from a filename
# if combine==True, then a mono data is returned (either using just mono, or averaging L and R)
# else, return both L and R (duplicating if the file has only 1 track)
def fromfile(filename, combine=False):
    w = wave.open(filename, 'r')
    
    channels, samplebytes, samplehz, samples, _, __ = w.getparams()

    framedata = w.readframes(samples)

    w.close()
    
    if samplebytes == 1:
        adata = np.fromstring(framedata, dtype=np.int8)
    elif samplebytes == 2:
        adata = np.fromstring(framedata, dtype=np.int16)
    elif samplebytes == 3:
        # since there is no 24 bit format, we have to combine int8 's, this may create problems
        print ("warning, 24 bit wave support may be buggy!")
        u8data = np.fromstring(framedata, dtype=np.int8)
        u8pdata = u8data.astype(np.int32)
        assert(len(u8data) % 3 == 0)
        # combine, assuming little endian
        adata = u8pdata[0::3] + 256 * u8pdata[1::3] + (256 ** 2) * u8data[2::3]
    elif samplebytes == 4:
        adata = np.fromstring(framedata, dtype=np.int32)
    else:
        adata = np.fromstring(framedata, dtype=np.float32)

    # normalize to [-1.0, 1.0]
    adata = adata.astype(np.float32) / (2.0 ** (8 * samplebytes-1))

    # heads up so people know what's going on
    print ("read from file " + filename)

    # logic to return data in the format they asked for, if they ask for combine, we will always return np.ndarray
    # else, return tuple of two np.ndarray s
    if channels == 2:
        if combine:
            return (adata[0::2] + adata[1::2]) / 2.0
        else:
            return (adata[0::2], adata[1::2])
    else:
        if combine:
            return adata
        else:
            return (adata, adata)


# outputs l and r audio to a wav file
def tofile(filename, _laudio, _raudio=None, hz=44100):
    wout = wave.open(filename, 'w')
    wout.setparams((2, 2, hz, 0, 'NONE', 'not compressed'))

    laudio = _laudio[:]

    # either duplicate left to create stereo
    if _raudio is None:
        raudio = laudio[:]
    # or use provided
    else:
        raudio = _raudio[:]
    
    # scale 
    out = np.empty((2 * len(laudio),), dtype=np.int16)

    normed = normalize((laudio, raudio))
    
    # this will cast and round
    out[0::2] = 32767 * normed[0]
    out[1::2] = 32767 * normed[1]

    wout.writeframes(out.tostring())
    wout.close()
    
    print ("wrote to file " + filename)
    

