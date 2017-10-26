"""

input and output operations

"""

import chaudio
import numpy as np

import wave


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

    # logic to return data in the format they asked for, if they ask for combine, we will always return np.ndarray
    # else, return tuple of two np.ndarray s

    return chaudio.Source(adata, channels=channels, hz=samplehz)

    #if _normalize:
    #    v = normalize(v)

    #return v


# outputs Source 
def tofile(filename, _audio):
    audio = chaudio.util.raw.normalize(chaudio.Source(_audio)).reformat(channels=2, dtype=np.int16)

    wout = wave.open(filename, 'w')
    wout.setparams((2, 2, audio.hz, 0, 'NONE', 'not compressed'))

    raw_data = chaudio.flatten(audio)
#    audio = combine(audio, channels=2)

    # scale 
    #out = np.empty((2 * len(audio[0]),), dtype=np.int16)

    #normed = normalize(audio)
    
    # this will cast and round
    #out[0::2] = 32767 * normed[0]
    #out[1::2] = 32767 * normed[1]

    wout.writeframes(raw_data.tostring())
    wout.close()
    
    chaudio.msgprint("wrote to file " + filename)
    









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
    


