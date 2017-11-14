"""Musical Track (:mod:`chaudio.track`)
====================================================

.. currentmodule:: chaudio.track


"""

import chaudio

class Note(object):

    def __init__(self, offset=(0, 0), freq="A4", t=None, **kwargs):
        self.offset = offset
        self._freq = freq
        self.t = t
        self.kwargs = kwargs

    def get_freq(self):
        if isinstance(self._freq, str):
            return chaudio.util.note(self._freq)
        else:
            return self._freq

    def set_freq(self, freq):
        self._freq = freq
    
    freq = property(get_freq, set_freq)

    def __str__(self):
        return "Note (offset=%s, freq=%s, t=%s, %s)" % (self.offset, self._freq, self.t, self.kwargs)

    __repr__ = __str__


class Track(object):

    def __init__(self, notes=None, timesignature=None):
        if notes is None:
            notes = []

        if timesignature is None:
            timesignature = chaudio.defaults["timesignature"]

        self.notes = notes
        self.timesignature = timesignature

    def add_note(self, *args, **kwargs):
        if len(args) > 0:
            if isinstance(args[0], Note):
                for arg in args:
                    if not isinstance(arg, Note):
                        raise ValueError("If giving Note values in add_note, all must be notes!")
                    self.notes += [arg]
            else:
                self.notes += [Note(*args, **kwargs)]
        else:
            raise ValueError("Note arguments are empty!")

    def play(self, instrument):
        arranger = chaudio.arrangers.ExtendedArranger(timesignature=self.timesignature, setitem="beat")
        
        for note in self.notes:
            if note.t is None:
                t = note.t
            else:
                t = chaudio.times(self.timesignature[note.t], hz=arranger._source.hz)
            arranger[note.offset] = instrument.note(freq=note.freq, t=t, **note.kwargs)

        return arranger.source

    def shift(self, offset=(0, 0)):
        for note in self.notes:
            if isinstance(note.offset, tuple):
                if isinstance(offset, tuple):
                    note.offset = (note.offset[0] + offset[0], note.offset[1] + offset[1])
                else:
                    note.offset = (note.offset[0], note.offset[1] + offset)
            else:
                if isinstance(offset, tuple):
                    note.offset = (note.offset + offset[0], note.offset + offset[1])
                else:
                    note.offset += offset








