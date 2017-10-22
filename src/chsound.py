"""

general utilities


"""


import numpy as np
import wave
import struct
import soundfile

# returns an array of times lasting for `t` seconds, sampled at `hz` per second (default 44100)
def times(t, hz=44100):
    return np.arange(0, t, 1.0 / hz)

# returns a normalized audio between -1.0 and 1.0
def normalize(source):
    return source / abs(max(np.max(source), np.min(source), key=abs))

# returns audiodata from a filename
def fromfile(filename):
    w = wave.open(filename, 'r')
    for i in range(w.getnframes()):
        frame = w.readframes(i)
        print (frame)
    w.close()


def tofile(filename, laudio, raudio=None, hz=44100):
    wout = wave.open(filename, 'w')
    wout.setparams((2, 2, hz, 0, 'NONE', 'not compressed'))

    out = np.empty((2 * len(laudio),), dtype=np.int16)
    out[0::2] = 32767 * normalize(laudio)

    if raudio is not None:
        out[1::2] = 32767 * normalize(raudio)
    else:
        out[1::2] = out[0::2]

    wout.writeframes(out.tostring())
    wout.close()
    

