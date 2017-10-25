"""

common utilities for chaudio

"""

import chaudio

import codecs
import wave

import numpy as np

# returns max of absolute value
def maxabs(data):
    return np.max(np.abs(data[:]))


valid_note_names = {
    "Ab": 25.95654359874657, 
    "A": 27.5, 
    "A#": 29.13523509488062, 
    "Bb": 29.13523509488062, 
    "B": 30.867706328507758, 
    "C": 32.70319566257483,
    "C#": 34.64782887210901, 
    "Db": 34.64782887210901, 
    "D": 36.70809598967595, 
    "D#": 38.890872965260115, 
    "Eb": 38.890872965260115, 
    "E": 41.20344461410874, 
    "F": 43.653528929125486, 
    "F#": 46.2493028389543, 
    "Gb": 46.2493028389543, 
    "G": 48.99942949771866,
    "G#": 51.91308719749314, 
}

valid_octaves = [0, 1, 2, 3, 4, 5, 6, 7, 8]

def note(name):
    note_name = ""
    for i in name:
        if not i.isdigit():
            note_name += i
        else:
            break
    octave_number = name.replace(note_name, "")

    if octave_number == "":
        octave_number = 4
    else:
        octave_number = int(octave_number)

    if note_name not in valid_note_names.keys():
        raise ValueError("invalid note name: %s" % (note_name))

    if octave_number not in valid_octaves:
        raise ValueError("invalid octave number: %s" % (octave_number))

    return valid_note_names[note_name] * (2.0 ** octave_number)
    


# returns an array of times
def times(ar, hz=44100):
    # if ar is just a time value (in seconds, return array based on that)
    if isinstance(ar, float) or isinstance(ar, int):
        return np.arange(0, ar, 1.0 / hz)
    # else, assume it is sample data and return resulting arange based on that
    else:
        return times(float(len(ar)) / hz, hz)

# returns numpy arrays from the audio
# handles mono and stereo
def flatten(audio):
    if isinstance(audio, tuple):
        return audio[0][:], audio[1][:]
    else:
        return audio[:]

# returns a single array 
def interleave(_audio):
    audio = flatten(_audio)
    if isinstance(audio, tuple):
        ret = np.empty((2 * len(audio[0]), ), dtype=audio[0].dtype)
        ret[0::2] = audio[0]
        ret[1::2] = audio[1]
        return ret
    else:
        return audio

# returns a normalized audio between -1.0 and 1.0
def normalize(audio):
    # stereo input
    if isinstance(audio, tuple):
        l = audio[0][:]
        r = audio[1][:]
        to_div = max(maxabs(l), maxabs(r))
        if to_div != 0:
            return l / to_div, r / to_div
        else:
            return l, r
    else:
        _audio = audio[:]
        return _audio / maxabs(_audio)

# combines audio into a number of channels
def combine(audio, channels=1):
    # channels need to be averaged
    if channels == 1:
        if type(audio) == tuple:
            return (audio[0][:] + audio[1][:]) / 2.0
        else:
            return audio[:]
    elif channels == 2:
        if type(audio) == tuple:
            return audio[:]
        else:
            return (audio[:], audio[:])
    else:
        raise ValueError("channels must be 1 or 2")

# cents are a measurement of pitch change, +1200 cents = 1 octave, +100 = half step (like C to C#)
def transpose(hz, cents=0):
    return hz * 2.0 ** (cents / 1200.0)

"""

internal data scheme:

dtype should be np.float32 when passing through stdout

The string should be like this:

"dtype=<dtype>,channels=<channels>:<NUMPY DATA STRING>"

like (default):

"dtype=np.float32,channels=2:<HEX>"

"""


def fromdatastr(wavestring):
    _meta = wavestring[:wavestring.index(":")]
    _dtype, _channels = _meta.split(",")
    channels = int(_channels.replace("channels=", ""))
    _dtype = _dtype.replace("dtype=", "")

    if _dtype == "np.float32":
        dtype = np.float32
    elif _dtype == "np.int16":
        dtype = np.int16
    else:
        chaudio.msgprint("warning, unknown data type, assuming np.float32")
        dtype = np.float32

    eframedata = wavestring[wavestring.index(":")+1:]

    sframedata64 = eframedata.encode("utf-8")
    sframedata = codecs.decode(sframedata64, 'base64')

    framedata = np.fromstring(sframedata, dtype=dtype)
    
    if channels == 2:
        return (framedata[0::2], framedata[1::2])
    else:
        return framedata

def todatastr(_data, channels=2, _dtype=np.float32):
    data = interleave(combine(_data, channels=channels))
    conv = None

    if _dtype == np.float32:
        dtype = "np.float32"
        conv = 1.0
    elif _dtype == np.int16:
        dtype = "np.int16"
        conv = (2.0 ** 15 - 1)
    else:
        chaudio.msgprint("warning, unknown data type, assuming np.float32")
        dtype = "np.float32"
        conv = 1.0
    
    wavedata = (conv * data).astype(_dtype).tostring()
    wavestr64 = codecs.encode(wavedata, 'base64')
    wavestr = wavestr64.decode('utf-8')

    return "dtype=%s,channels=%s:%s" % (dtype, channels, wavestr)
    


# returns audiodata from a filename
# if combine==True, then a mono data is returned (either using just mono, or averaging L and R)
# else, return both L and R (duplicating if the file has only 1 track)
def fromfile(filename, _channels=1, _normalize=False):
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
        chaudio.msgprint("warning, 24 bit wave support may be buggy!")
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

    if channels == 2:
        adata = (adata[0::2], adata[1::2])

    # heads up so people know what's going on
    chaudio.msgprint("read from file " + filename)

    # logic to return data in the format they asked for, if they ask for combine, we will always return np.ndarray
    # else, return tuple of two np.ndarray s

    v = combine(adata, channels=_channels)

    if _normalize:
        v = normalize(v)

    return v


# outputs l and r audio to a wav file
def tofile(filename, _audio, hz=44100):
    wout = wave.open(filename, 'w')
    wout.setparams((2, 2, hz, 0, 'NONE', 'not compressed'))

    audio = flatten(_audio)
    audio = combine(audio, channels=2)

    # scale 
    out = np.empty((2 * len(audio[0]),), dtype=np.int16)

    normed = normalize(audio)
    
    # this will cast and round
    out[0::2] = 32767 * normed[0]
    out[1::2] = 32767 * normed[1]

    wout.writeframes(out.tostring())
    wout.close()
    
    chaudio.msgprint("wrote to file " + filename)
    





