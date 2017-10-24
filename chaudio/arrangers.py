"""

arrangemers, which serve to combine and multiplex audio

"""

import chaudio
from chaudio import plugins

import numpy as np


# simple datastructure for storing inputs so that they can be recreated
class InsertCall:
    def __init__(self, key, val, kwargs):
        self.key = key
        self.val = val
        self.kwargs = kwargs

    def __hash__(self):
        return hash(self.key) + hash(np.sum(self.val[:])) + hash(frozenset(self.kwargs))

    def __str__(self):
        return "Insert(%s, %s, %s)" % (self.key, self.val, self.kwargs)

    def __repr__(self):
        return self.__str__()


"""

this class is for combining sounds together, given a point, and applying plugins:

Only has support for inputting at a number of samples

"""

class Arranger:

    # constructor, accepts nothing by default
    def __init__(self, **kwargs):

        # store these for later
        self.kwargs = kwargs

        # start off data as empty
        self.data = np.zeros((0,), dtype=np.float32)

        # keep track of tracks that were inserted
        self.insert_calls = []

        # a list of plugins to apply to incoming audio (should be of type BasicAudioPlugin)
        self.insert_plugins = []
        self.final_plugins = []

        self.last_hash = -1

        self.source_init()

    # returns kwarg passed, or default if none is there
    def getarg(self, key, default=None):
        if key in self.kwargs:
            return self.kwargs[key]
        else:
            return default

    # method to tell whether the class has changed
    def __hash__(self):
        return hash(tuple(self.insert_calls)) + hash(tuple(self.insert_plugins)) + hash(tuple(self.final_plugins))

    # for printing out
    def __str__(self):
        return "%s, args=%s, insert_plugins: %s, final_plugins: %s" % (type(self).__name__, self.kwargs, self.insert_plugins, self.final_plugins)

    def __repr__(self):
        return self.__str__()


    # this is used by things that extend Arranger
    def source_init(self, **kwargs):
        pass

    # returns the index of the plugin added
    def add_insert_plugin(self, plugin):
        self.insert_plugins += [plugin]
        return len(self.insert_plugins) - 1

    # returns the index of the plugin added
    def add_final_plugin(self, plugin):
        self.final_plugins += [plugin]
        return len(self.final_plugins) - 1

    # removes either an index (if input is int) or a plugin
    def remove_insert_plugin(self, plugin):
        if isinstance(plugin, int):
            self.insert_plugins.pop(plugin)
        else:
            self.insert_plugins.remove(plugin)

    # removes either an index (if input is int) or a plugin
    def remove_final_plugin(self, plugin):
        if isinstance(plugin, int):
            self.final_plugins.pop(plugin)
        else:
            self.final_plugins.remove(plugin)


    # applies the insert call to the object's data array
    def apply_insert(self, insert_call):
        key = insert_call.key
        val = insert_call.val[:]
        kwargs = insert_call.kwargs

        for plugin in self.insert_plugins:
            val = plugin.process(val)
        
        if len(self.data) < key+len(val):
            self.data = np.append(self.data, 
                                  np.zeros((key + len(val) - len(self.data), ), 
                                  dtype=np.float32)
            )

        self.data[key:key+len(val)] += val

    # ensures self.data contains the most up to date arrangement of all inserts, returns True if something changed
    def ensure_updated_data(self):
        cur_hash = hash(self)
        if cur_hash != self.last_hash:
            self.update_data()
            self.last_hash = hash(self)
            return True
        else:
            return False
    
    # ensures the final data (data + final_plugins) is up to date, returns True if something changed
    def ensure_updated_final_data(self):
        chash = hash(self)
        if self.ensure_updated_data() or chash != self.last_hash:
            self.update_final_data()
            self.last_hash = hash(self)
            return True
        else:
            return False

    # recalculates self.data (you probably shouldn't use this method, use ensure_updated_data to avoid recalculating)
    def update_data(self):
        self.data = np.empty((0,), dtype=np.float32)

        for insert_call in self.insert_calls:
            self.apply_insert(insert_call)
            
    # recalculates self.final_data (you probably shouldn't use this method, use ensure_updated_final_data to avoid recalculating)
    def update_final_data(self):
        self.final_data = self.data[:]


        for plugin in self.final_plugins:
            self.final_data = plugin.process(self.final_data)


    # adds 'data' to self.data, offset by sample
    def insert_sample(self, sample, _data, **kwargs):
        # make sure it is a positive int
        if not isinstance(sample, int):
            raise TypeError("Arranger insert_sample, sample must be int")
        if sample < 0:
            raise KeyError("Arranger insert_sample, sample must be > 0")

        # create a new insert call so that this can be recalculated
        self.insert_calls += [InsertCall(sample, _data, kwargs)]

        #self.ensure_updated_data()


    # the default setitem call (arrange[key] = _val)
    def __setitem__(self, key, _val):
        self.insert_sample(key, _val)
        
    # treats the arrangement as a numpy array
    def __getitem__(self, key):
        self.ensure_updated_final_data()
        return self.final_data[key]

    # treats the arrangement as a numpy array
    def __len__(self):
        self.ensure_updated_final_data()
        return self.final_data.__len__()


class ExtendedArranger(Arranger):

    def source_init(self, **kwargs):
        self.hz = self.getarg("hz", 44100)
        self.timesignature = self.getarg("timesignature", chaudio.TimeSignature())
        self.setitem_type = self.getarg("setitem", "time")

        self.setitem_funcs = { 
            "sample": self.insert_sample,
            "time": self.insert_time,
            "beat": self.insert_beat
        }

    def insert_time(self, t, _data):
        self.insert_sample(int(self.hz * t), _data)

    def insert_beat(self, beat, _data):
        self.insert_time(self.timesignature[beat], _data)

    def __setitem__(self, key, _data):
        if self.setitem_type in self.setitem_funcs:
            self.setitem_funcs[self.setitem_type](key, _data)
        else:
            raise Exception("setitem_type (%s) is not a valid setitem function type" % (self.setitem_type))




    


