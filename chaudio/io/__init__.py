"""

input output functions

"""

import chaudio
import numpy as np
import wave
import io



# class for file specification, really only for internal usage
class WaveFormat(object):

    def __init__(self, name, dtype, samplewidth, scale_factor):
        self.name = name
        self.dtype = dtype
        self.samplewidth = samplewidth
        self.scale_factor = scale_factor


formats = {}

formats["8i"] = WaveFormat("8i", np.int8, 1, 2.0 ** 7 - 1)
formats["16i"] = WaveFormat("16i", np.int16, 2, 2.0 ** 15 - 1)
formats["24i"] = WaveFormat("24i", np.int32, 3, 2.0 ** 23 - 1)
formats["32i"] = WaveFormat("32i", np.int32, 4, 2.0 ** 31 - 1)

# does not work properly
#formats["32f"] = WaveFormat("32f", np.float32, 4, 1.0)


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
def tofile(filename, _audio, waveformat="16i", normalize=True):
    audio = chaudio.source.Source(_audio, dtype=np.float32)
    #audio.channels = 2

    if type(waveformat) is str:
        waveformat = formats[waveformat]

    if normalize:
        audio = chaudio.util.raw.normalize(audio)

    wout = wave.open(filename, 'w')
    wout.setparams((audio.channels, waveformat.samplewidth, audio.hz, 0, 'NONE', 'not compressed'))

    # pad the data with L,R,L,R
    raw_data = np.zeros((len(audio) * audio.channels, ), dtype=waveformat.dtype)

    for i in range(0, audio.channels):
        raw_data[i::audio.channels] = waveformat.scale_factor * audio[i][:]

    if waveformat.name == "24i":
        chaudio.msgprint("24 bit support is spotty!")
        tmp_data = [None] * 3
        for i in range(0, 3):
            tmp_data[i] = (raw_data // (256 ** i)) % 256

        raw_data = np.zeros((3 * len(raw_data), ), np.int8)
        for i in range(0, 3):
            raw_data[i::3] = tmp_data[i]


    # tostring() returns byte data, just like it is stored by WAV format
    wout.writeframes(raw_data.tostring())
    wout.close()
    
    # a message so users know what's happening
    chaudio.msgprint("wrote to file " + filename)
    

