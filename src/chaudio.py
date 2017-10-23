"""

general utilities


"""

import numpy as np
import wave
import struct
import waveforms
import math
import plugins
import logging

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
def normalize(data):
    return data / maxabs(data)


"""

this class is for combining sounds together, given a point:

"""

class SetitemCall:
    def __init__(self, key, val, kwargs):
        self.key = key
        self.val = val
        self.kwargs = kwargs


class BasicAudioSource:
    def __init__(self, hz=44100):
        self.hz = hz
        self.samplestep = 1.0 / self.hz

        self.data = np.empty((0,), dtype=np.float32)

        self.setitem_calls = []

        # a list of plugins to apply to incoming audio (should be of type BasicAudioPlugin)
        self.setitem_plugins = []
        self.final_plugins = []

        self.last_setitem_hash = -1
        self.last_final_hash = -1

        self.source_init()

    def __hash__(self):
        print ("hasing")
        return hash(np.sum(self.data) + sum([np.sum(i.val[:]) for i in self.setitem_calls]))
        #return hash(math.sin(len(self.setitem_calls) * 1.0 + .5 * len(self.setitem_plugins) + 3.2 * len(self.final_plugins))) + hash(np.sum(self.data)) + hash(np.sum([i.val[:] for i in self.setitem_calls])) + hash(tuple(self.setitem_plugins)) + hash(tuple(self.final_plugins))

    def source_init(self):
        pass

# returns the index of the plugin added

    def add_setitem_plugin(self, plugin):
        self.setitem_plugins += [plugin]
        return len(self.setitem_plugins) - 1

    def add_final_plugin(self, plugin):
        self.final_plugins += [plugin]
        return len(self.final_plugins) - 1

    def remove_setitem_plugin(self, plugin):
        if isinstance(plugin, int):
            self.setitem_plugins.pop(plugin)
        else:
            self.setitem_plugins.remove(plugin)

    def remove_final_plugin(self, plugin):
        if isinstance(plugin, int):
            self.final_plugins.pop(plugin)
        else:
            self.final_plugins.remove(plugin)


# recalculate

    def apply_setitem(self, setitem_call):
        key = setitem_call.key
        val = setitem_call.val[:]

        kwargs = setitem_call.kwargs

        for plugin in self.setitem_plugins:
            val = plugin.process(val)
        
        if len(self.data) < key+len(val):
            self.data = np.append(self.data, 
                                  np.zeros((key + len(val) - len(self.data), ), 
                                  dtype=np.float32)
            )

        self.data[key:key+len(val)] += val

    def ensure_updated_data(self):
        cur_hash = self.__hash__()
        #print ([i.val for i in self.setitem_calls])
        if cur_hash != self.last_setitem_hash:
            #print([i.val for i in self.setitem_calls])
            self.update_data()
            self.last_setitem_hash = cur_hash
            return True
        else:
            return False

    def ensure_updated_final_data(self):
        if self.ensure_updated_data() or hash(tuple(self.final_plugins)) != self.last_final_hash:
            self.update_final_data()
            self.last_final_hash = hash(tuple(self.final_plugins))
            return True
        else:
            return False

    def update_data(self):
        #print ("updating data...")
        
        self.data = np.empty((0,), dtype=np.float32)

        for setitem_call in self.setitem_calls:
            self.apply_setitem(setitem_call)
        #print ("done")
            

    def update_final_data(self):
        #print ("updating final data...")
        self.final_data = self.data[:]

        for plugin in self.final_plugins:
            self.final_data = plugin.process(self.final_data)

        #print ("done")


    def __setitem__(self, key, _val, **kwargs):
        if not isinstance(key, int):
            raise TypeError("in AudioSource __getitem__, key should be int")

        if key < 0:
            raise KeyError("AudioSource key must be > 0")

        val = _val[:]


        new_setitem = SetitemCall(key, _val, kwargs)
        self.setitem_calls += [new_setitem]

        if not self.ensure_updated_data():
            self.apply_setitem(new_setitem)

    # adds 'data' to self.data, offset by sample
    def insert(self, data, sample):
        self[sample] = data

    # inserts data at a given time
    def insert_time(self, data, time):
        self.insert(data, int(time * self.hz))

    def __getitem__(self, key):
        self.ensure_updated_final_data()
        return self.final_data[key]

    def __len__(self):
        self.ensure_updated_final_data()
        return self.final_data.__len__()


class SmoothedSignalAudioSource(BasicAudioSource):

    def source_init(self, *args, **kwargs):
        self.add_setitem_plugin(plugins.SmoothPlugin())



# returns audiodata from a filename
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
        # since there is no 24 bit format, we have to combine int8 's
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

    adata = adata.astype(np.float32) / (2.0 ** (8 * samplebytes-1))

    print ("read from file " + filename)

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



def tofile(filename, _laudio, _raudio=None, hz=44100):
    wout = wave.open(filename, 'w')
    wout.setparams((2, 2, hz, 0, 'NONE', 'not compressed'))

    laudio = _laudio[:]
    if _raudio is None:
        raudio = laudio[:]
    else:
        raudio = _raudio[:]

    out = np.empty((2 * len(laudio),), dtype=np.int16)
    out[0::2] = 32767 * normalize(laudio)
    out[1::2] = 32767 * normalize(raudio)


    wout.writeframes(out.tostring())
    wout.close()
    
    print ("wrote to file " + filename)
    

