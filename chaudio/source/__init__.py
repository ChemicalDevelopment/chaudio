"""Audio Source (:mod:`chaudio.source`)
===================================================

.. currentmodule:: chaudio.source


All these are essentially abstractions above a data array of samples.

Has support for variable number of channels, any samplerate, and data type

Operators are overriden, so that you can apply them to a constant, numpy array, or other audio source

When you set a property (like source.hz or source.channels), the internal data is updated automatically.

"""

import numpy as np

import scipy
import scipy.signal

import chaudio


class Source(object):
    """Represents the default audio source, with variable number of channels and samplerate


    """

    # initialize, given any data, and optionally hz and dtype (which are determined based on 'data', or chaudio defaults)
    def __init__(self, data, hz=None, dtype=None):
        """Source creation routine

        Creates a Source consisting of ``data``.

        If ``data`` is a np.ndarray, assume that these are raw sample data, taken at ``hz`` samplerate (if none is given, ``44100``). If no ``dtype`` is given, default to ``data.dtype``

        If ``data`` is a tuple or list, assume that it contains channel data, and set the number of channels to the length of the tuple/list, and each individual channel to the np.ndarray at the corresponding index.

        If ``data`` is :class:`chaudio.source.Source`, copy it, but apply the ``hz`` and ``dtype`` parameters for the new format. If ``hz`` isn't given, use ``data.hz`` as the default, and do the same with ``dtype`` and ``data.dtype``.

        If ``data`` is :class:`chaudio.arrangers.Arranger`, calculate its data, and turn into a source.

        If ``data`` is a chaudio class, resample the data to ``hz``. Otherwise, assume it is the input was sampled at ``hz`` per second.

        Parameters
        ----------
        data : np.ndarray, :class:`chaudio.source.Source`, :class:`chaudio.arrangers.Arranger`, tuple, list
            Describes how to gather data. See 

        beats : int, float
            Number of beats (or pulses) per measure
        
        division : int, float
            Note division that represents a single pulse

        bpm : int, optional
            The speed, in beats per minute

        """

        if issubclass(type(data), Source):
            # if we are creating a Source from another Source, just essentially copy it
            self._data = data.copy_data()
            self._channels = data.channels
        elif type(data) in (tuple, list):
            # if we are given a python tuple or list, we assume that it contains the channels of data
            assert(len(data) >= 1)
            self._data = list(data)
        elif type(data) is np.ndarray:
            # assume a mono input
            self._data = [data]
        elif issubclass(type(data), chaudio.arrangers.Arranger):
            # if it is an arranger, treat it like we passed in it's source
            self._data = data.source.copy_data()
            self._channels = data.source.channels
        else:
            raise Exception("Don't know how to convert '%s' into '%s'" % (type(data).__name__, type(self).__name__))

        # only try to determine hz if we were not given any
        if hz is None:
            if issubclass(type(data), Source):
                # just copying an existing source's hz
                self._hz = data.hz
            elif issubclass(type(data), chaudio.arrangers.Arranger):
                # copy it as if we passed in the arranger's source
                self._hz = data.source.hz
            else:
                # return a default
                self._hz = chaudio.defaults["hz"]
        else:
            # explicitly given, so just outright set it
            self._hz = hz

        # only try to determine dtype if we were not given any
        if dtype is None:
            if issubclass(type(data), Source):
                # just copying an existing source's dtype
                self._dtype = data.dtype
            elif issubclass(type(data), chaudio.arrangers.Arranger):
                # act as if we passed in the arranger's source
                self._dtype = data.source.dtype
            elif type(data) is np.ndarray:
                # the numpy array stores this info, so try that
                self._dtype = data.dtype
            else:
                # return a default (this should be a float-like type)
                self._dtype = chaudio.defaults["dtype"]
        else:
            # explicitly given
            self._dtype = dtype
    
        # this self.dtype forces the internal data to update, so leave this here
        self.dtype = self._dtype

    # returns a copy (so that any mutations done will not affect the original)
    def copy(self):
        """Returns a copy of the item

        Returns
        -------
        :class:`chaudio.source.Source`
            An exact copy of the current object

        """
        return type(self)(self.copy_data(), self.hz)
    
    # copies just the internal data as a list of channel data
    def copy_data(self):
        """Returns a copy of the raw sample data

        Returns
        -------
        list of np.ndarray
            Channels with np.ndarray 's describing the sample data

        """
        r = [None] * self.channels
        for i in range(0, self.channels):
            r[i] = np.copy(self.data[i])
        return r

    def resample(self, tohz):
        """Internally adjust the sample rate in a smart way (using FFT and IFFT)

        This doesn't return anything, so it changes the object it's called on. To return a new source, and not change the one being called, use :meth:`chaudio.source.Source.resampled`

        Parameters
        ----------
        tohz : int, float
            The sample rate, in samples per second

        """
        self.hz = tohz

    def resampled(self, tohz):
        """Returns a copy of the current object resampled to ``tohz``

        To not make a copy, and instead alter the object in place, use :meth:`chaudio.source.Source.resample`

        Parameters
        ----------
        tohz : int, float
            The sample rate, in samples per second

        Returns
        -------
        :class:`chaudio.source.Source`
            A copy of the object resampled to ``tohz`` samplerate

        """
        res = self.copy()
        res.resample(tohz)
        return res

    def rechannel(self, tochannels):
        """Internally adjust how many channels are stored

        This doesn't return anything, so it changes the object it's called on. To return a new source, and not change the one being called, use :meth:`chaudio.source.Source.rechanneled`

        If ``tochannels == self.channels``, no change is made. Else, the behaviour is thus:

        If ``tochannels == 1`` (which means ``self.channels == 2``), the new data array contains 1 item, which is the average of the previous two channels. This will roughly sound the same (as in if you have any sounds that are purely in one channel or the other, they will still be heard).

        If ``tochannels == 2`` (which means ``self.channels == 1``), the new data array is the old one, but duplicated.

        To return an altered copy, and not change the object itself, use :meth:`chaudio.source.Source.rechanneled`

        Parameters
        ----------
        tochannels : { 1, 2 }
            The number of channels the source should have. Must be ``1`` or ``2``.
            

        """
        self.channels = tochannels

    def rechanneled(self, tochannels):
        """Return a copy of the object, with a specified number of channels

        To not make a copy, and instead alter the object in place, use :meth:`chaudio.source.Source.rechannel`

        Parameters
        ----------
        tochannels : { 1, 2 }
            The number of channels the source should have. Must be ``1`` or ``2``.

        Returns
        -------
        :class:`chaudio.source.Source`
            A copy of the object with the number of channels changed to ``tochannels``

        """

        res = self.copy()
        res.channels = tochannels
        return res

    def redtype(self, todtype):
        """Internally adjust what data format is used

        This probably shouldn't be used by your application, as it does not rescale values. It's main use is in the :mod:`chaudio.util` module, for outputting as WAVE data.

        Changes the internal data format

        To make a copy, and not alter the current object, use :meth:`chaudio.source.Source.redtyped`

        Parameters
        ----------
        todtype : { np.int8, np.int16, np.int32, np.float32, np.float16 }
            Numpy data format
            

        """
        self.dtype = todtype

    def redtyped(self, todtype):
        """Return a copy of the object, with a specified internal data format

        To not make a copy, and instead alter the object in place, use :meth:`chaudio.source.Source.redtype`

        Parameters
        ----------
        todtype : { np.int8, np.int16, np.int32, np.float32, np.float16 }
            Numpy data format

        Returns
        -------
        :class:`chaudio.source.Source`
            A copy of the object with the data format changed to ``todtype``

        """

        res = self.copy()
        res.dtype = todtype
        return res


    # return list of channel data
    def get_data(self):
        return self._data
    
    # sets the data, and must be a list or tuple of channel data
    def set_data(self, v):
        assert(type(v) in (list, tuple))
        self._data = list(v)

    data = property(get_data, set_data)


    # returns the internal data format
    def get_dtype(self):
        return self._dtype

    # essentially casts the internal data to the new type
    def set_dtype(self, v):
        for i in range(0, self.channels):
            self.data[i] = self.data[i].astype(v)
        self._dtype = v

    dtype = property(get_dtype, set_dtype)


    # _channels is no variable, so it is determined by the length of the list of channel data
    def get_channels(self):
        return len(self.data)
    
    # this may need support for more than 2 channels (which is probably not used anyways)
    def set_channels(self, v):
        # only these are supported, as of now (not sure how's the best way to handle other cases)
        assert(v in (1, 2))
        if v != self.channels:
            # we know that our channels is 1 if v = 2, and 2 if v = 1
            if v == 1:
                assert(len(self.data) == 2)
                # average the data, so that we don't lose any parts.
                # TODO: perhaps add configuration kwarg (and chaudio.defaults) for a method to decrease number of channels?
                self.data = [(self.data[0] + self.data[1]) / 2.0]
            else:
                assert(len(self.data) == 1)
                # just duplicate the single channel we already have
                self.data = [self.data[0], self.data[0]]
    
    channels = property(get_channels, set_channels)


    # return sample rate (in samples / second)
    def get_hz(self):
        return self._hz

    # will automatically resample the internal array
    def set_hz(self, v):
        if self.hz != v:
            for i in range(0, self.channels):
                # TODO: consider adding optimized methods for resampling to an integer multiple of the old samplerate
                # this method internally probably will end up using FFT most of the time, and will thus be time consuming for large inputs
                self.data[i] = scipy.signal.resample(self.data[i], int(len(self.data[i]) * v / self._hz))
            
            self._hz = v

    hz = property(get_hz, set_hz)

    
    # returns a floating point value representing the length of this source in seconds
    def get_seconds(self):
        return float(self.samples) / self.hz
    
    def set_seconds(self):
        # this is called when someone tries: source.seconds = 2
        # this isn't supported, because it is not the function of source to provide high level functionality, such as autoresizing
        raise Exception("seconds is not a settable property!")

    seconds = property(get_seconds, set_seconds)


    # returns how many samples all the channels last (all channels should be equal length)
    def get_samples(self):
        # all channels should be the same length, so we check that
        agree_len = len(self.data[0])
        for i in range(1, len(self.data)):
            if agree_len != len(self.data[i]):
                # people should never see this
                raise Exception("internal error: channels have different length (please report this issue!)")
        # if all are the same, return the length they agree at
        return agree_len

    def set_samples(self, v):
        # this isn't supported, because it's not needed. Instead, use source.ensure(samples)
        # there should not be a property (such as samples) that can internally append or change length. Only methods should handle that
        raise Exception("samples is not a settable property!")

    samples = property(get_samples, set_samples)


    # overriding methods

    # string representation, showing channels, samples, and samplerate
    def __str__(self):
        return "Source[%s] %sl %.2fs %shz" % (self.channels, self.samples, self.seconds, self.hz)

    # returns length in samples
    def __len__(self):
        return self.samples

    # use like source[channel:index] (channel can be : for all channels, like source[:,0])
    # this returns either a numpy array or tuple/list of numpy arrays (for multiple channels)
    # source[N,X] acts like self.data[N][X] (N and X can be anything), which is a list of channels with X applied to each
    # source[N] is the same as source.data[N]
    def __getitem__(self, key):
        """Return a portion of the data in a source

        If ``key`` is an int or slice, return the channels indicated, in list format. So, use ``source[:]`` to return all channels as a list, or ``source[0]`` for the 0th channel (which is left on a stereo source).

        If ``key`` is a tuple, return all the channels represented by ``source[key[0]]`` subscripted with ``key[1]``. So, ``source[0, :5]`` returns the first 5 samples of the ``0``th channel. ``source[:, :5]`` returns a list of the first 5 values for each channel.

        Parameters
        ----------
        key : int, slice, tuple
            If int or slice, return the channels represented by ``key``. If it's a tuple, return channel[key[1]] for each channel represented by ``key[0]``. See examples for more info.

        Returns
        -------
        list of np.ndarray or np.ndarray
            If the ``key`` specified a single channel, return just that channel's specified data as np.ndarray. If multiple channels are indicated, return a list of channel data.

        """

        assert(type(key) in (int, tuple, slice))
        if type(key) is tuple:
            # it has multiple keys, so return them each channel with the key applied
            assert(len(key) == 2)
            k0 = self.data[key[0]]
            if type(k0) is not list:
                return k0[key[1]]
            else:
                return [i[key[1]] for i in k0]
        else:
            # they are asking for a specific channel, so just give them a channel
            return self.data[key]


    # source[N] = V sets the Nth channel to V, which should be a numpy array
    # source[N,X] = V is tricky logic, but tries to emulate the inverse of __getitem__
    # thus, in general the assumed function of source.__setitem__(k, v) should work like this:
    # source.__setitem__(k, source.__getitem__(k)) means source does not functionally change
    # however, this also supports setting to another Source, although this is still expiremental
    def __setitem__(self, key, val):
        """Set a portion of the data in a source

        If ``key`` is an int or slice, set the channels indicated, in list format. So, use ``source[:] = y`` to set channels to a y, which must be a list of np.ndarray. 

        If ``key`` is a tuple, set all the channels represented by ``source[key[0]]`` subscripted with ``key[1]``  to ``val``. So, ``source[0, :5] = y`` sets the first five values of the ``0``th channels to y. Note that ``y`` must be either a constant, or have the same shape as the values it is replacing. In our example, ``y`` would have to be a constant, or a np.ndarray with length 5

        In general, the following should hold for any source ``x``, key ``key``, and value ``val``:

        >>> x[key] = val
        >>> print (x[key] == val)
        True


        Parameters
        ----------
        key : int, slice, tuple
            If int or slice, set the channel data represented by ``key``. If it's a tuple, set channel[key[1]] for each channel represented by ``key[0]``. See examples for more info.

        val : int, float, list, tuple, np.ndarray
            The value to set the specified samples to. If it is a list, tuple, or np.ndarray, it must be the same shape as the values it is replacing. So, if saying ``x[0, :5] = y``, ``y`` must be int, float, or ``len(y)`` must be 5.


        Returns
        -------
        list of np.ndarray or np.ndarray
            If the ``key`` specified a single channel, return just that channel's specified data as np.ndarray. If multiple channels are indicated, return a list of channel data.

        """


        assert(type(key) in (int, tuple, slice))
        if type(key) is tuple:
            if issubclass(type(val), Source):
                # warn them
                chaudio.msgprint("warning: using __setitem__ with a Source value on a Source object may give unexpected results")
                valc = val.copy()
                valc.channels = self.channels
                valc.hz = self.hz
                self.data[key[0]][key[1]] = valc
            else:
                rs = self.data[key[0]]
                if not isinstance(rs, list):
                    self.data[key[0]] = val
                else:
                    for x in rs:
                        x[key[1]] = val
        else:
            # they are asking for a specific channel
            self.data[key] = val

    # this inserts something at an offset (in samples)
    def insert(self, offset, _val):
        """Inserts samples at a given offset

        To return a copy and not modify the original object, use :meth:`chaudio.source.Source.inserted`.

        This clears ``data[offset:offset+len(_val)]``, and sets it to ``_val``

        Parameters
        ----------
        offset : int
            What sample to insert at

        _val : numpy.ndarray, :class:`chaudio.source.Source`, :class:`chaudio.arrangers.Arranger`
            This is converted to a source internally, see :meth:`chaudio.source.Source.__init__` for details on how this is done.

        """

        val = Source(_val)
        val.hz = self._hz
        val.channels = self.channels
        # ensure we have enough room
        self.ensure(length=offset + len(val))

        # loop through and insert them (replacing data at that position)
        for i in range(0, self.channels):
            self._data[i][offset:offset+len(val)] = val._data[i]

    def inserted(self, offset, _val):
        """Returns a copy with inserted samples at a given offset

        To not make a copy, and rather edit inplace, use :meth:`chaudio.source.Source.insert`.

        Parameters
        ----------
        offset : int
            What sample to insert at

        _val : numpy.ndarray, :class:`chaudio.source.Source`, :class:`chaudio.arrangers.Arranger`
            This is converted to a source internally, see :meth:`chaudio.source.Source.__init__` for details on how this is done.

        Returns
        -------
        :class:`chaudio.source.Source`
            A copy of the object with the ``data[offset:offset+len(_val)]`` assigned to ``_val``.

        """

        res = self.copy()
        res.insert(offset, _val)
        return res

    # plops in _v before the existing self._data
    def prepend(self, _val):
        """Prepend values to the data array

        To return a copy and not modify the original object, use :meth:`chaudio.source.Source.prepended`.

        This sets ``self.data`` to ``_val`` and ``data`` concatenated. This essentially can be used to add delays, silence, or prepend any other data

        Parameters
        ----------

        _val : numpy.ndarray, :class:`chaudio.source.Source`, :class:`chaudio.arrangers.Arranger`
            This is converted to a source internally, see :meth:`chaudio.source.Source.__init__` for details on how this is done.

        """

        v = Source(_val)
        v.hz = self.hz
        v.channels = self.channels
        for i in range(0, self.channels):
            self._data[i] = np.append(v.data[i], self._data[i])

    # returns a copy
    def prepended(self, _val):
        """Returns a copy with prepended values to the data array

        To modify the original object and not make a copy, use :meth:`chaudio.source.Source.prepend`.

        This returns a copy of the object called on, with ``_val`` prepended before it.

        Parameters
        ----------

        _val : numpy.ndarray, :class:`chaudio.source.Source`, :class:`chaudio.arrangers.Arranger`
            This is converted to a source internally, see :meth:`chaudio.source.Source.__init__` for details on how this is done.

        Returns
        -------
        :class:`chaudio.source.Source`
            ``_val`` and the object called with concatenated

        """
        r = self.copy()
        r.prepend(_val)
        return r

    # appends _v after the existing self._data
    def append(self, _val):
        """Append values to the data array

        To return a copy and not modify the original object, use :meth:`chaudio.source.Source.appended`.

        This sets ``self.data`` to ``data`` and ``_val`` concatenated. This tacks on ``_val`` to the end.

        Parameters
        ----------

        _val : numpy.ndarray, :class:`chaudio.source.Source`, :class:`chaudio.arrangers.Arranger`
            This is converted to a source internally, see :meth:`chaudio.source.Source.__init__` for details on how this is done.

        """

        v = Source(_val)
        v.hz = self.hz
        v.channels = self.channels
        for i in range(0, self.channels):
            self._data[i] = np.append(self._data[i], v.data[i])

    # returns a copy
    def appended(self, _val):
        """Returns a copy of the object with values appended to the data array

        To not make a copy, and instead modify the object called with, use :meth:`chaudio.source.Source.append`.

        Parameters
        ----------

        _val : numpy.ndarray, :class:`chaudio.source.Source`, :class:`chaudio.arrangers.Arranger`
            This is converted to a source internally, see :meth:`chaudio.source.Source.__init__` for details on how this is done.

        Returns
        -------
        :class:`chaudio.source.Source`
            A copy of the current object, but with ``_val`` appended.

        """
        
        r = self.copy()
        r.append(_val)
        return r

    def ensure(self, length=None):
        """Makes sure that the source is a certain length, which will append 0's to the end if needed

        To return a copy and not modify the original object, use :meth:`chaudio.source.Source.ensured`.

        Parameters
        ----------

        _val : numpy.ndarray, :class:`chaudio.source.Source`, :class:`chaudio.arrangers.Arranger`
            This is converted to a source internally, see :meth:`chaudio.source.Source.__init__` for details on how this is done.

        """

        if length is not None and length > len(self._data[0]):
            needed_len = length - len(self._data[0])
            pad = np.zeros((needed_len, ), dtype=self.dtype)
            for i in range(0, self.channels):
                self._data[i] = np.append(self._data[i], pad)

    # returns a copy
    def ensured(self, length=None):
        """Makes a copy that is guaranteed to be a certain length, which will append 0's to the end if needed

        To modify the original object, use :meth:`chaudio.source.Source.ensure`.

        Parameters
        ----------

        _val : numpy.ndarray, :class:`chaudio.source.Source`, :class:`chaudio.arrangers.Arranger`
            This is converted to a source internally, see :meth:`chaudio.source.Source.__init__` for details on how this is done.

        Returns
        -------
        :class:`chaudio.source.Source`
            A copy of the object being called, but it is guaranteed to be of a certain length

        """
        r = self.copy()
        r.ensure(length=length)
        return r

    # returns what to operate on channels with any operator
    def __opit__(self, v):
        if issubclass(type(v), Source):
            v.hz = self.hz
            v.channels = self.channels
            return v.data
        elif issubclass(type(v), chaudio.arrangers.Arranger):
            return self.__opit__(v.source)
        elif type(v) is np.ndarray:
            return [v] * self.channels
        else:
            r = [np.array([v] * self.samples, dtype=self.dtype)] * self.channels
            return r

    # all operators are distributed if float/int, or paired if arrays
    def __add__(self, _v):
        r = self.copy()
        v = self.__opit__(_v)
        for i in range(0, self.channels):
            r.data[i] += v[i]
        return r

    def __sub__(self, _v):
        r = self.copy()
        v = self.__opit__(_v)
        for i in range(0, self.channels):
            r.data[i] -= v[i]
        return r

    def __mul__(self, _v):
        r = self.copy()
        v = self.__opit__(_v)
        for i in range(0, self.channels):
            r.data[i] *= v[i]
        return r

    def __div__(self, _v):
        r = self.copy()
        v = self.__opit__(_v)
        for i in range(0, self.channels):
            r.data[i] /= (v[i])
        return r

    def __truediv__(self, _v):
        r = self.copy()
        v = self.__opit__(_v)
        for i in range(0, self.channels):
            r.data[i] /= v[i]
        return r

    def __floordiv__(self, _v):
        r = self.copy()
        v = self.__opit__(_v)
        for i in range(0, self.channels):
            r.data[i] //= v[i]
        return r

    def __mod__(self, _v):
        r = self.copy()
        v = self.__opit__(_v)
        for i in range(0, self.channels):
            r.data[i] %= v[i]
        return r

    def __pow__(self, _v):
        r = self.copy()
        v = self.__opit__(_v)
        for i in range(0, self.channels):
            r.data[i] **= v[i]
        return r


    __radd__ = __add__
    __rsub__ = __sub__
    __rmul__ = __mul__
    __rdiv__ = __div__
    __rtruediv__ = __truediv__
    __rfloordiv__ = __floordiv__
    __rmod__ = __mod__
    __rpow__ = __pow__


class Mono(Source):
    def __init__(self, data, hz=None):
        """A source with only 1 channel

        Returns
        -------
        :class:`chaudio.source.Mono`
            The same as using :meth:`chaudio.source.Source.__init__`, but then ensures there is only 1 channel

        """

        super().__init__(data, hz)
        self.channels = 1

    def set_channels(self, v):
        raise Exception("Can not set channels on a %s source!" % type(self).__name__)


class Stereo(Source):
    def __init__(self, data, hz=None):
        """A source with only 2 channels

        Returns
        -------
        :class:`chaudio.source.Stereo`
            The same as using :meth:`chaudio.source.Source.__init__`, but then ensures there is only 2 channel

        """

        super().__init__(data, hz)
        self.channels = 2

    def set_channels(self, v):
        raise Exception("Can not set channels on a %s source!" % type(self).__name__)





