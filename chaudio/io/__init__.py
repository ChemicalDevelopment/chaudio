"""

input output functions

"""

import chaudio
import numpy as np
import wave
import io

# string data read from
# essentially treat `strdata` as WAV file contents 
def fromstring(strdata, *args, **kwargs):
    return fromfile(io.StringIO(strdata), *args, **kwargs)


def tostring(_audio, *args, **kwargs):
    strdata = io.StringIO()
    tofile(strdata, _audio, *args, **kwargs)
    return strdata.getvalue()

# returns an AudioSource from a filename
# if combine==True, then a mono data is returned (either using just mono, or averaging L and R)
# else, return both L and R (duplicating if the file has only 1 track)
def fromfile(filename):
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

    # heads up so people know what's going on
    chaudio.msgprint("read from file " + filename)

    channel_data = [None] * channels
    for i in range(0, channels):
        channel_data[i] = adata[i::channels]

    return chaudio.source.Source(channel_data, hz=samplehz)


# outputs Source 
def tofile(filename, _audio, normalize=True):
    audio = chaudio.source.Source(_audio, hz=44100, dtype=np.float32)
    audio.channels = 2

    if normalize:
        audio = chaudio.util.raw.normalize(audio)

    wout = wave.open(filename, 'w')
    wout.setparams((2, 2, audio.hz, 0, 'NONE', 'not compressed'))

    # scaling factor
    scale_factor = 2.0 ** 15 - 1.0

    # pad the data with L,R,L,R
    raw_data = np.zeros((len(audio) * audio.channels, ), dtype=np.int16)
    for i in range(0, audio.channels):
        raw_data[i::audio.channels] = scale_factor * audio[i][:]

    # tostring() returns byte data, just like it is stored by WAV format
    wout.writeframes(raw_data.tostring())
    wout.close()
    
    # a message so users know what's happening
    chaudio.msgprint("wrote to file " + filename)
    

