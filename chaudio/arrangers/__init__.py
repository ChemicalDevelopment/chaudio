"""

essentially multiplexers and plugin chains

Can record inputs, and detect if they change, and regenerate their source automatically

This is essentially "smart" JIT audio production

An Arranger can have another Arranger inserted, and it will keep track of whether the sources have changed, only recalculating if needed.

"""


import chaudio

import numpy as np


# simple datastructure for storing inputs so that they can be recreated, and detected if they change
class InsertCall(object):
    def __init__(self, key, val, kwargs):
        self.key = key
        self.val = val
        self.kwargs = kwargs

    # should return different value if anything changed
    def __hash__(self):
        return hash(self.key) + hash(np.sum(np.array(self.val[:]) ** 2)) + hash(frozenset(self.kwargs))

    # simple string form
    def __str__(self):
        return "Insert(%s, %s, %s)" % (self.key, self.val, self.kwargs)
    
    __repr__ = __str__



"""

this class is for combining sounds together, given a point, and applying plugins:

Only has support for inputting at a number of samples, serves as a base class.abs

ExtendedArranger is probably the best for most users

"""

class Arranger(object):

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

        # keep track of hash so we know whether we need to update
        self.last_hash = -1


    # getter setters that ensure the internal source is updated
    def get_source(self):
        self.ensure_updated_source()
        return self._source

    def set_source(self, v):
        raise Exception("cannot set Arranger's source")

    source = property(get_source, set_source)


    # returns kwarg passed, or default if no kwarg is given
    def getarg(self, key, default=None):
        if key in self.kwargs:
            return self.kwargs[key]
        else:
            return default
    
    # sets the kwargs value
    # if replace is False, check if key is already set. If so, do not replace value
    def setarg(self, key, val, replace=True):
        if replace or (key not in self.kwargs):
            self.kwargs[key] = val


    # method to tell whether the class has changed
    def __hash__(self):
        return hash(tuple(self.insert_calls)) + hash(tuple(self.insert_plugins)) + hash(tuple(self.final_plugins))

    # for printing out values
    def __str__(self):
        return "%s, len=%ss, args=%s, insert_plugins: %s, final_plugins: %s, hash: %s" % (type(self).__name__, self.source.seconds, self.kwargs, self.insert_plugins, self.final_plugins, hash(self))

    __repr__ = __str__

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

    # applies the insert call to the object's internal source
    def apply_insert(self, insert_call):
        key = insert_call.key
        val = chaudio.source.Source(insert_call.val)
        val.hz = self._source.hz
        val.channels = self._source.channels
        kwargs = insert_call.kwargs

        for plugin in self.insert_plugins:
            val = plugin.process(val)
        
        if len(self._source[0]) < key + len(val):
            self._source.ensure(length=key+len(val))

        for i in range(0, self._source.channels):
            self._source[i,key:key+len(val)] += val[i]

    # ensures source is updated, returns true if it required an update
    def ensure_updated_source(self):
        chash = hash(self)
        if chash != self.last_hash:
            self.update_source()
            self.last_hash = hash(self)
            return True
        else:
            return False


    # force updates the source. No other classes should call this method; the arranger class figures out if it needs to update
    def update_source(self):
        hz, channels, dtype = int(self._source.hz), int(self._source.channels), self._source.dtype
        self._source = chaudio.Source(np.empty((0, )), hz=hz, dtype=dtype)
        self._source.channels = channels
        
        for insert_call in self.insert_calls:
            self.apply_insert(insert_call)

        for plugin in self.final_plugins:
            self._source = plugin.process(self._source)

        self._source.dtype = dtype
        self._source.hz = hz
        self._source.channels = channels


    # adds 'data' to self.source, offset by sample
    def insert_sample(self, sample, _data, **kwargs):
        # make sure it is a positive int
        if not isinstance(sample, int):
            raise TypeError("Arranger insert_sample, sample must be int")
        if sample < 0:
            raise KeyError("Arranger insert_sample, sample must be > 0")

        # create a new insert call so that this can be recalculated, even though it is not instantly computed.
        # this is because it works like a JIT compiler
        self.insert_calls += [InsertCall(sample, _data, kwargs)]


    # the default setitem call (arrange[key] = _val)
    def __setitem__(self, key, _val):
        self.insert_sample(key, _val)
        
    # essentially an aliase for self.source.__getitem__, but it ensures source is updated
    def __getitem__(self, key):
        self.ensure_updated_source()
        return self.source[key]

    # treats the arrangement as a numpy array
    def __len__(self):
        self.ensure_updated_source()
        return self.source.__len__()

"""

lke arranger, but supports beats and time inserts

"""

class ExtendedArranger(Arranger):

    def __init__(self, **kwargs):
        # this weird super call is required for python2+python3 compatability
        super(ExtendedArranger, self).__init__(**kwargs)

        self.setarg("hz", chaudio.defaults["hz"], replace=False)
        self.setarg("timesignature", chaudio.defaults["timesignature"], replace=False)
        self.setarg("setitem", "sample", replace=False)

        # different function methods to apply to insert commands (using exar[a] = b)
        self.setitem_funcs = { 
            "sample": self.insert_sample,
            "time": self.insert_time,
            "beat": self.insert_beat
        }

    # inserts _data at a time (in seconds) t
    def insert_time(self, t, _data):
        self.insert_sample(int(self.getarg("hz") * t), _data)

    # inserts at a beat, which the internal timesignature should handle and return a time for
    def insert_beat(self, beat, _data):
        self.insert_time(self.getarg("timesignature")[beat], _data)

    # finds out which method we are using, then applies it
    def __setitem__(self, key, _data):
        if self.getarg("setitem") in self.setitem_funcs:
            self.setitem_funcs[self.getarg("setitem")](key, _data)
        else:
            raise Exception("setitem type '%s' is not a valid setitem function type" % (self.getarg("setitem")))
