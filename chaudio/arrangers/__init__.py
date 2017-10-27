"""

essentially multiplexors and plugin chains

"""

import chaudio

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
        self._source = chaudio.source.Source(np.empty((0, )))

        # keep track of tracks that were inserted
        self.insert_calls = []

        # a list of plugins to apply to incoming audio (should be of type BasicAudioPlugin)
        self.insert_plugins = []
        self.final_plugins = []

        self.last_hash = -1

        self.source_init()

    def get_source(self):
        self.ensure_updated_source()
        return self._source

    def set_source(self, v):
        raise Exception("cannot set Arranger's source")

    source = property(get_source, set_source)


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
        return "%s, len=%s, args=%s, insert_plugins: %s, final_plugins: %s" % (self.source.seconds, type(self).__name__, self.kwargs, self.insert_plugins, self.final_plugins)

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
        val = chaudio.source.Source(insert_call.val)
        val.hz = self._source.hz
        val.channels = self._source.channels
        kwargs = insert_call.kwargs

        for plugin in self.insert_plugins:
            val = plugin.process(val)
        
        if len(self._source[0]) < key+len(val):
            self._source.ensure(length=key+len(val))

        for i in range(0, self._source.channels):
            self._source[i,key:key+len(val)] += val[i]

    # ensures source is updated, returns true if it needed to update
    def ensure_updated_source(self):
        chash = hash(self)
        if chash != self.last_hash:
            self.update_source()
            self.last_hash = hash(self)
            return True
        else:
            return False


    # force updates the source
    def update_source(self):
        self._source = chaudio.Source(np.empty((0, )))

        for insert_call in self.insert_calls:
            self.apply_insert(insert_call)

        for plugin in self.final_plugins:
            self._source = plugin.process(self._source)


    # adds 'data' to self.source, offset by sample
    def insert_sample(self, sample, _data, **kwargs):
        # make sure it is a positive int
        if not isinstance(sample, int):
            raise TypeError("Arranger insert_sample, sample must be int")
        if sample < 0:
            raise KeyError("Arranger insert_sample, sample must be > 0")

        # create a new insert call so that this can be recalculated
        self.insert_calls += [InsertCall(sample, _data, kwargs)]


    # the default setitem call (arrange[key] = _val)
    def __setitem__(self, key, _val):
        self.insert_sample(key, _val)
        
    # treats the arrangement as a numpy array
    def __getitem__(self, key):
        self.ensure_updated_source()
        return self.source[key]

    # treats the arrangement as a numpy array
    def __len__(self):
        self.ensure_updated_source()
        return self.source.__len__()







class ExtendedArranger(Arranger):

    def source_init(self, **kwargs):
        self.hz = self.getarg("hz", 44100)
        self.timesignature = self.getarg("timesignature", chaudio.util.TimeSignature())
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




    




