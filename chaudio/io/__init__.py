"""Input/Output functionality (:mod:`chaudio.io`)
==============================================

.. currentmodule:: chaudio.io

Allows any data type to be stored to a file, returned as a string, read from a file or string, and other I/O issues.

At this point, only WAVE integer formats are accepted, so 8 bit, 16 bit, 24 bit, and 32 bit WAVE formats all work. 

WAVE 32f format does not work.

In the future, support for ``.ogg`` and ``.mp3`` files will be hopefully added.


"""


# wave is part of the standard library, and supports WAVE integer formats
import wave
import io

import chaudio
import numpy as np


# class for file specification, really only for internal usage
# TODO: make this so that people can write their own
class WaveFormat(object):

    def __init__(self, name, dtype, samplewidth, scale_factor):
        self.name = name
        self.dtype = dtype
        self.samplewidth = samplewidth
        self.scale_factor = scale_factor


# holds wave format specifiers
formats = {}

formats["8i"] = WaveFormat("8i", np.int8, 1, 2.0 ** 7 - 1)
formats["16i"] = WaveFormat("16i", np.int16, 2, 2.0 ** 15 - 1)
formats["24i"] = WaveFormat("24i", np.int32, 3, 2.0 ** 23 - 1)
formats["32i"] = WaveFormat("32i", np.int32, 4, 2.0 ** 31 - 1)


def play(_audio, waveformat="16i"):
    """Plays the audio through the system speaker

    Requires simpleaudio ``pip3 install simpleaudio`` to work (which is a dependency of chaudio)

    Parameters
    ----------

    _audio : :class:`chaudio.source.Source`, :class:`chaudio.arrangers.Arranger`, np.ndarray
        This is converted to :class:`chaudio.source.Source`, and then output.

    waveformat : str, :class:`chaudio.io.WaveFormat`
        This describes how to convert the data. Should probably be an integer format, and the default is good enough for anyone. See :class:`chaudio.io.WaveFormat` for how to use it.

    """

    import simpleaudio as sa
    import atexit

    audio = chaudio.source.Source(_audio, dtype=np.float32)


    # detect wave format
    if type(waveformat) is str:
        waveformat = formats[waveformat]

    raw_data = audio[:]

    for i in range(0, len(raw_data)):
        raw_data[i] = (waveformat.scale_factor * chaudio.util.normalize(raw_data[i])).astype(waveformat.dtype)

    # this is packed
    play_buf = np.zeros(len(raw_data) * len(raw_data[0]), dtype=waveformat.dtype)

    for i in range(0, len(raw_data)):
        play_buf[i::len(raw_data)] = raw_data[i]

    play_obj = sa.play_buffer(play_buf, len(raw_data), waveformat.samplewidth, audio.hz)

    atexit.register(play_obj.wait_done)


def fromfile(filename):
    """Returns file contents of a WAVE file (either name or file pointer) as a :class:`chaudio.source.Source`

    Note that they are not "normalized" as in using :meth:`chaudio.util.normalize`, but rather simply converted from the internal WAVE formats (which are integers), and divided by the maximum integer of that size. That way, all WAVE formats will return (within rounding) the same result when called with this function, so the original volume is conserved. This is the behaviour audacity has when reading files, which is to convert to 32f format internally.

    This supports all standard WAVE integer formats, 8 bit, 16 bit, 24 bit, and 32 bit.

    Note that WAVE 32f format is **NOT** supported yet

    Parameters
    ----------
    filename : str, file
        If a string, that file is opened, or if it is a file object already (which can be an io.StringIO object), that is used instead of opening another.

    Returns
    -------
    :class:`chaudio.source.Source`
        A chaudio Source class, with appropriate channels, samplerate, and a dtype of float32

    """
    
    w = wave.open(filename, 'r')
    
    channels, samplebytes, samplehz, samples, _, __ = w.getparams()

    framedata = w.readframes(samples)

    w.close()
    
    # cast from string, numpy essentially handles most of it for us
    if samplebytes == 1:
        adata = np.fromstring(framedata, dtype=np.int8)
    elif samplebytes == 2:
        adata = np.fromstring(framedata, dtype=np.int16)
    elif samplebytes == 3:
        # since there is no 24 bit format, we have to combine int8 's
        # this has only been tested on a few computers, but it should work on any machine, given WAVE specifications
        chaudio.msgprint("warning: 24 bit wave support may be buggy!")
        u8data = np.fromstring(framedata, dtype=np.int8)
        u8pdata = u8data.astype(np.int32)
        assert(len(u8data) % 3 == 0)
        # combine, assuming little endian
        adata = u8pdata[0::3] + 256 * u8pdata[1::3] + (256 ** 2) * u8data[2::3]
    elif samplebytes == 4:
        adata = np.fromstring(framedata, dtype=np.int32)
    else:
        chaudio.msgprint("warning: sample width is not 1, 2, 3, or 4 (I read in '%s'). I will try my best to read this!" % samplebytes)
        u8data = np.fromstring(framedata, dtype=np.int8)
        u8pdata = u8data.astype(np.int64)
        assert(len(u8data) % samplebytes == 0)
        adata = sum([u8pdata[i::samplebytes] * (256 ** i) for i in range(0, samplebytes)])

    # normalize to [-1.0, 1.0]
    adata = adata.astype(np.float32) / (2.0 ** (8 * samplebytes-1))

    # heads up so people know what's going on
    chaudio.msgprint("read from file " + filename)

    channel_data = [None] * channels
    for i in range(0, channels):
        channel_data[i] = adata[i::channels]

    return chaudio.source.Source(channel_data, hz=samplehz)
    
def fromstring(strdata, *args, **kwargs):
    """Treat the input as WAVE file contents, and return a :class:`chaudio.source.Source`.

    Parameters
    ----------
    strdata : str
        Treat ``strdata`` as the WAVE file contents

    Returns
    -------
    :class:`chaudio.source.Source`
        A chaudio Source class, with appropriate channels, samplerate, and a dtype of float32

    """
    return fromfile(io.StringIO(strdata), *args, **kwargs)


def tofile(filename, _audio, waveformat="16i", normalize=True):
    """Output some sort of audio to a file (which can be a name or file pointer).

    Always to WAVE format, and specify ``waveformat`` in order to change what kind. Default, it is 16 bit integer (CD quality).

    Parameters
    ----------
    filename : str, file
        If a string, that file is opened, or if it is a file object already (which can be an io.StringIO object), that is used instead of opening another.
    
    _audio : np.ndarray, :class:`chaudio.source.Source`, :class:`chaudio.source.Arranger`
        Casts ``_audio`` to a :class:`chaudio.source.Source`, which will work on any chaudio type. You shouldn't have to worry about this, it stays truthful to the input.

    waveformat : { '8i', '16i', '24i', '32i' }
        Describes the number of bits per sample, and what type of data to write ('i' is integer).

    normalize : bool
        Whether or not to normalize before writing. This should be the default, to avoid any clipping.


    """

    audio = chaudio.source.Source(_audio, dtype=np.float32)

    # detect wave format
    if type(waveformat) is str:
        waveformat = formats[waveformat]

    # this should be a default
    if normalize:
        audio = chaudio.util.normalize(audio)

    # use python wave library
    wout = wave.open(filename, 'w')
    wout.setparams((audio.channels, waveformat.samplewidth, audio.hz, 0, 'NONE', 'not compressed'))

    # pad the data with L,R,L,R
    raw_data = np.zeros((len(audio) * audio.channels, ), dtype=waveformat.dtype)

    for i in range(0, audio.channels):
        raw_data[i::audio.channels] = (waveformat.scale_factor * audio[i][:]) // 1

    # special care must be taken to pack the values as u8 's
    if waveformat.name == "24i":
        chaudio.msgprint("warning: 24 bit wave support may be buggy!")
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
    

def tostring(_audio, *args, **kwargs):
    """Returns the WAVE file contents. Essentially returns what :meth:`chaudio.io.tofile` would have written to a file.

    Parameters
    ----------

    _audio : np.ndarray, :class:`chaudio.source.Source`, :class:`chaudio.source.Arranger`
        Casts ``_audio`` to a :class:`chaudio.source.Source`, which will work on any chaudio type. You shouldn't have to worry about this, it stays truthful to the input.

    waveformat : { '8i', '16i', '24i', '32i' }
        Describes the number of bits per sample, and what type of data to write ('i' is integer).

    normalize : bool
        Whether or not to normalize before writing. This should be the default, to avoid any clipping.

    Returns
    -------
    str
        An str representing the WAVE file contents.

    """

    strdata = io.StringIO()
    tofile(strdata, _audio, *args, **kwargs)
    return strdata.getvalue()

