"""Instruments (:mod:`chaudio.instruments`)
==============================================

.. currentmodule:: chaudio.instruments

Support for instrument plugins that can play notes, MIDI data, and other formats

"""

import chaudio

from chaudio.util import ensure_lr_dict

class Instrument(object):
    """

    Base class to extend if you have an instrument

    """
    
    def __init__(self, **kwargs):
        """Initializes an Instrument (which is a base class that should not be used, please use :class:`chaudio.instruments.Oscillator` or another class!)

        Parameters
        ----------
        **kwargs : (key word arguments)
            The generic instrument arguments

        Returns
        -------
        :class:`chaudio.instruments.Instrument`
            A generic instrument object

        """
        self.kwargs = kwargs

    def merged_kwargs(self, specific_kwargs):
        """Returns the merged kwargs (i.e. the input replaces values not specified as defaults.)

        Parameters
        ----------
        specific_kwargs : dict
            What was passed to the specific function (like :meth:`chaudio.instruments.Instrument.note`) that needs to override the initialiezd kwargs.

        Returns
        -------
        dict
            The merged results, with anything from ``specific_kwargs`` taking precedence over the defaults

        """

        ret = self.kwargs
        for key in specific_kwargs:
            ret[key] = specific_kwargs[key]
        
        return ret

    def __getitem__(self, key):
        """Returns the configuration/kwargs value at a specified key

        Parameters
        ----------
        key : obj
            Whatever key the value was stored as (typically str)

        Returns
        -------
        obj
            The value stored as a kwarg

        """

        return self.kwargs.__getitem__(key)

    def __setitem__(self, key, val):
        """Sets the configuration/kwargs value at a specified key to a provided value

        Parameters
        ----------
        key : obj
            Whatever key the value was stored as (typically str)

        val : obj
            What value to set at ``key``

        """
        return self.kwargs.__setitem__(key, val)

    def note(self, **kwargs):
        pass


class Oscillator(Instrument):
    """

    Represents a basic oscillator, which is the base class for most synths

    """

    def __init__(self, waveform=chaudio.waves.sin, amp=1.0, samplerate=None, phase_shift=0, freq_shift=0, tweak=None, pan=0, **kwargs):
        """Initializes an oscillator, given waveform and a host of other parameters

        
        Keep in all parameters can be overriden in individual calls to the :meth:`chaudio.instruments.oscillator.note` function. So, to override the ``phase_shift`` for a single note, run like ``osc.note("A4", phase_shift=2) to temporarily override the initialized parameter.

        To change the values you initialized with, set like so: ``osc["phase_shift"] = 2``

        Parameters that accept a ``tuple`` and ``dict`` (such as ``phase_shift``) mean that it can accept left and right values that differ. So, the left channel has a different phase offset than the right side. If you give a tuple for these values, ``v[0]`` is for the left and ``v[1]`` is for the right. If given a dict, ``v["left"]`` is for the left and ``v["right"]`` is for the right. And remember, all parameters accept a single value as a float/int/None, in which the left and right values are both taken as ``v``.

        Parameters
        ----------
        waveform : func
            What internal waveform to generate sounds based on. See module :mod:`chaudio.waves` for a list of defaults included with chaudio, as well as their function.

        amp : float, int
            the amplitude of the waveform. This is useful when combining multiple oscillators (see :class:`chaudio.instruments.MultiOscillator` for example on this).
        
        samplerate : int, None
            What is the samplerate that should be used
        
        phase_shift : float, tuple, dict
            The offset in the wavefunction. A phase shift of 0 means use the default waveform function. A phase shift of .5 means begin halfway through the first oscillation.
        
        freq_shift : float, tuple, dict
            The offset, in cents, that the oscillator transposes given notes to. Essentially, if given ``freq`` to play, the returned source containing data is the note ``freq`` transposed ``freq_shift`` cents.

        tweak : float, None, tuple, dict
            The tweak value to apply on the waveform.
        
        pan : float, None
            A panning (Left/Right) value to change the offset in the stereo space. -1.0 representing all the way left, +1.0 representing all the way right.

        Returns
        -------
        :class:`chaudio.instruments.Oscillator`
            The instrument object

        """
        kwargs["waveform"] = waveform
        kwargs["amp"] = amp
        kwargs["samplerate"] = samplerate
        kwargs["phase_shift"] = phase_shift
        kwargs["freq_shift"] = freq_shift
        kwargs["tweak"] = tweak
        kwargs["pan"] = pan
        super(Oscillator, self).__init__(**kwargs)


    def __str__(self):
        return "Oscillator (%s)" % ", ".join([k + "=" + (self.kwargs[k].__name__ if hasattr(self.kwargs[k], "__name__") else str(self.kwargs[k])) for k in self.kwargs])

    __repr__ = __str__

    def note(self, **kwargs):
        """Returns the result of the instrument performing a note for specified parameters

        Basic usage is ``osc.note(freq="A4", amp=.5, ...)`` and that overrides the ``amp`` value set on creation.

        You can permanently update these values with ``osc["amp"] = .5`` to update the default used if nothing is passed into the note function.

        Parameters
        ----------
        freq : int, float, str, np.ndarray
            This can be a frequency directly, or a string of a note name (see :meth:`chaudio.util.note` for what is suppoerted). Additionally, it can be an array of frequencies at time values. Note that this should contain data with the sameplerate as the oscillator. You can check the oscillator sample rate with: ``osc["samplerate"]``. As a consequence, it also needs to be the same shape as the time parameter ``t`` generated array
        
        kwargs : (key word args)
            These are all values that can override the default values (which all are documented in the :meth:`chaudio.instruments.Oscillator.__init__` method). 

        Returns
        -------

        :class:`chaudio.source.Stereo`
            The source representing the oscillator playing the note

        """

        # fill current kwargs with defaults if they don't exist
        kwargs = self.merged_kwargs(kwargs)

        freq = kwargs["freq"]
        amp = kwargs["amp"]
        waveform = kwargs["waveform"]
        samplerate = kwargs["samplerate"]
        t = kwargs["t"]
        pan = kwargs["pan"]
            
        if isinstance(freq, str):
            freq = chaudio.util.note(freq)

        if isinstance(t, int) or isinstance(t, float):
            t = chaudio.times(t, samplerate)

        if isinstance(pan, int) or isinstance(pan, float):
            if pan < -1.0 or pan > +1.0:
                chaudio.msgprint("warning: pan value given was invalid! (err: pan=%s" % pan)
                if pan < -1.0:
                    pan = -1
                elif pan > 1.0:
                    pan = 1

        tweak = ensure_lr_dict(kwargs["tweak"])
        freq_shift = ensure_lr_dict(kwargs["freq_shift"])
        phase_shift = ensure_lr_dict(kwargs["phase_shift"])

        freq = ensure_lr_dict((
            chaudio.util.transpose(freq, freq_shift["left"]),
            chaudio.util.transpose(freq, freq_shift["right"])
        ))

        # scale it to (0, 1.0), 0 meaning all the way L, and 1.0 meaning all the way R
        adj_pan = (pan + 1) / 2.0

        data = {}

        for key in "left", "right":
            data[key] = amp * waveform(t + phase_shift[key] / freq[key], freq[key], tweak=tweak[key])

        res = chaudio.source.Stereo(((1 - adj_pan) * data["left"], adj_pan * data["right"]), samplerate)

        return res


class MultiOscillator(Instrument):
    """

    Similar to LMMS's triple oscillator (which itself was based on minimoog synth), but with a variable number

    """

    def __init__(self, osc=None, **kwargs):
        """Creates a MultiOscillator instrument


        """
        if osc is None:
            osc = [None] * 3
            osc[0] = Oscillator(waveform=chaudio.waves.square, samplerate=None, phase_shift=.4, freq_shift=-1200, tweak=.4, pan=-.6, amp=.55)
            osc[1] = Oscillator(waveform=chaudio.waves.triangle, samplerate=None, phase_shift=(.7, .5), freq_shift=(-508, -496), tweak=(.2, .45), pan=.4, amp=.3)
            osc[2] = Oscillator(waveform=chaudio.waves.saw, samplerate=None, phase_shift=(.1, .15), freq_shift=(1918, 1890), tweak=(.28, .35), pan=-.2, amp=.15)
        self.osc = osc
        self.kwargs = kwargs

    def __str__(self):
        return "MultiOscillator [\n%s\n]" % "\n".join(["    " + str(osc) for osc in self.osc])

    __repr__ = __str__


    def add_osc(self, osc):
        self.osc += [osc]

    def remove_osc(self, osc):
        if isinstance(osc, int):
            self.osc.pop(osc)
        else:
            self.osc.remove(osc)

    def note(self, **kwargs):
        # fill current kwargs with defaults if they don't exist
        for key in self.kwargs:
            if key not in kwargs:
                kwargs[key] = self.kwargs[key]

        res = None
        for i in self.osc:
            cosc = i.note(**kwargs)
            if res is None:
                res = cosc
            else:
                res += cosc
        return res


    def __getitem__(self, key):
        return self.osc.__getitem__(key)

    def __setitem__(self, key, val):
        self.osc.__setitem__(key)






