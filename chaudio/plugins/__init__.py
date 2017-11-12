"""Plugin Audio Processing (:mod:`chaudio.plugins`)
==============================================

.. currentmodule:: chaudio.plugins

These are plugins that take in an input, perform some action on it to alter the sound, and then return the result as a :class:`chaudio.source.Source`.

Some common ones:

.. autosummary::
    :toctree: submodules

    echo
    fade
    filters
    noise
    resolution
    volume


"""


# does nothing to audio, only stores it and retreives it, with hash to tell if it changed
class Basic(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __hash__(self):
        return hash(frozenset(self.kwargs.items()))

    def __str__(self):
        return "%s kwargs=%s" % (type(self).__name__, self.kwargs)

    __repr__ = __str__

    # the main method, this is called to actually perform on an object
    def process(self, _data):
        return _data

    # returns kwarg passed, or default if the dictionary does not contain it
    def getarg(self, key, default=None):
        if key in self.kwargs:
            return self.kwargs[key]
        else:
            return default

    # sets the kwargs[key] to val
    # if kwargs contains key already, will only replace it if replace=True
    def setarg(self, key, val, replace=True):
        if replace or key not in self.kwargs:
            self.kwargs[key] = val


from chaudio.plugins import (echo, fade, filters, noise, resolution, volume)

# aliases
Echo = echo.Echo
Fade = fade.Fade
Butter = filters.Butter
Noise = noise.Noise
Resolution = resolution.Resolution
Volume = volume.Volume


