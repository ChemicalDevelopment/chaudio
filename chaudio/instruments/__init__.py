"""Instruments (:mod:`chaudio.instruments`)
==============================================

.. currentmodule:: chaudio.instruments

Support for instrument plugins that can play notes, MIDI data, and other formats

"""

import chaudio
import numpy as np

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

    def raw_note(self, **kwargs):
        """Returns raw note source (i.e. without plugins added)

        MOST PEOPLE SHOULD NOT NEED THIS FUNCTION!

        Please use the :meth:`chaudio.instruments.Instrument.note` function for external needs, as this method is used internally there, and then plugins are applied.

        This method is not implemented in this base (i.e. :class:`chaudio.instruments.Instrument`) class, but should be implemented by any actual instrument.

        Parameters
        ----------
        **kwargs : (key word arguments)
            The generic instrument arguments

        Returns
        -------
        :class:`chaudio.source.Stereo`
            A source representing the raw note of the instrument (without plugins).

        """
        pass

    def note(self, **kwargs):
        """Returns raw note source with all plugins applied

        The `freq` argument is specified as the actual note being played. So, to play an ``A``, use ``instrument.note(freq="A", ...)``

        Parameters
        ----------
        **kwargs : (key word arguments)
            The generic instrument arguments (use `freq` for the note value)

        Returns
        -------
        :class:`chaudio.source.Stereo`
            A source representing instrument playing a note

        """
        raw_note_kwargs = self.merged_kwargs(kwargs, ["plugins"])
        res = self.raw_note(**raw_note_kwargs)
        for plugin in self.kwargs.get("plugins", {}):
            res = plugin.process(res)

        return res

    def add_plugin(self, plugin):
        """Adds a processing plugin

        Parameters
        ----------
        plugin : :class:`chaudio.plugins.Basic`
            Plugin object that extends Basic


        """
        if "plugins" in self.kwargs:
            self.kwargs["plugins"] += [plugin]
        else:
            self.kwargs["plugins"] = [plugin]


    def remove_plugin(self, plugin):
        """Removes a plugin, by the plugin object, or the index

        Parameters
        ----------
        plugin : :class:`chaudio.plugins.Basic` or int
            Plugin object that extends Basic, or index

        """

        if "plugins" in self.kwargs:
            if isinstance(plugin, int):
                self.kwargs["plugins"].pop(plugin)
            else:
                self.kwargs["plugins"].remove(plugin)
        else:
            raise KeyError("There are no plugins added yet!")



    def copy(self):
        """Returns a copy of the object

        Returns
        -------
        :class:`chaudio.instruments.Instrument` (or whatever class the object is)
            A copy of the object. Keeps the same type, however

        """
        return type(self)(self.kwargs.copy())

    def merged_kwargs(self, specific_kwargs, exclude=[]):
        """Returns the merged kwargs (i.e. the input replaces values not specified as defaults.) and then remove ``exclude`` vals.

        Parameters
        ----------
        specific_kwargs : dict
            What was passed to the specific function (like :meth:`chaudio.instruments.Instrument.note`) that needs to override the initialiezd kwargs.

        exclude : list, tuple
            Which arguments to remove (i.e. exclude) from the result

        Returns
        -------
        dict
            The merged results, with anything from ``specific_kwargs`` taking precedence over the defaults, then remove all from ``exclude``

        """

        ret = dict(self.kwargs)
        for key in specific_kwargs:
            ret[key] = specific_kwargs[key]

        for key in exclude:
            ret.pop(key, None)

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


class ADSREnvelope(object):
    """
    
    This is an `ADSR envelope <https://en.wikipedia.org/wiki/Synthesizer#Attack_Decay_Sustain_Release_.28ADSR.29_envelope>`_.

    For a good explanation, see `ADSR Envelope one wikiaudio <http://en.wikiaudio.org/ADSR_envelope>`_.

    .. image:: /resources/ADSR.png


    """
    def __init__(self, A=0, D=0, S=1, R=0):
        """Initializes the envelope with common parameters.

        Parameters
        ----------

        A : float
            'attack' value, in seconds. Essentially the envelope is ramping up until ``A`` seconds
        
        D : float
            'decay' value, in seconds. The envelope will scale gently to ``S`` between time ``A`` and ``A + D`` seconds.

        S : float
            'sustain' value, as an amplitude between 0.0 and 1.0. This is the value that the envelope holds between ``A + D`` and ``t - R`` seconds (where ``t`` is the length of the segment that is being enveloped).

        R : float
            'release', value in seconds. This is the time (from the end of the time values being enveloped) that the ADSR envelope starts fading out.


        """
        self.kwargs = {}

        self.kwargs["A"] = A
        self.kwargs["D"] = D
        self.kwargs["S"] = S
        self.kwargs["R"] = R

    def merged_kwargs(self, kwargs):
        res = self.kwargs.copy()
        for key in kwargs:
            res[key] = kwargs[key]
        return res

    def calc_val(self, t, **kwargs):
        """Returns the envelope values for a time sample array.

        This returns the values (which are all 0.0 to 1.0) of the envelope, applied over the times given in ``t``. The result has the same length as t, so that you can apply operations to ``t`` and others. See the examples below. This is used in :class:`chaudio.instruments.Oscillator`.

        Parameters
        ----------

        t : np.ndarray
            The value of time samples. These are generated (typically) using the :meth:`chaudio.util.times` method.

        kwargs : (key word args)
            These can override ``A``, ``D``, ``S``, or ``R`` for a specific call to this function without forever replacing the defaults.

        Returns
        -------
        
        np.ndarray
            A result with the same length as ``t`` (so you can do operations with them).


        Examples
        --------

        >>> t = chaudio.util.times(4)
        >>> wave = chaudio.waves.triangle(t, hz=220)
        >>> env = chaudio.instruments.ADSREnvelope(A=.4, D=1.0, S=.4, R=.8)
        >>> y = wave * env.calc_val(t)
        >>> # y now contains the wave with the envelope value
        >>> chaudio.play(y)

        """

        kwargs = self.merged_kwargs(kwargs)
        res = t.copy()

        if kwargs["A"] != 0:
            res[t <= kwargs["A"]] /= kwargs["A"]
        else:
            res[t <= kwargs["A"]] = 1

        delay_select = (t > kwargs["A"]) & (t <= kwargs["A"] + kwargs["D"])
        delay_t = t[delay_select]

        if len(delay_t) > 1:
            delay_min = delay_t[0]
            delay_max = delay_t[-1]
            res[delay_select] = 1.0 - (1.0 - kwargs["S"]) * (t[delay_select] - delay_min) / (delay_max - delay_min)
        else:
            res[delay_select] = 1.0


        sus_select = (t > kwargs["A"] + kwargs["D"]) & (t <= t[-1] - kwargs["R"])

        res[sus_select] = kwargs["S"]

        rel_select = (t > t[-1] - kwargs["R"])

        if len(t[rel_select]) > 1:
            rel_min = t[rel_select][0]
            rel_max = t[rel_select][-1]

            res[rel_select] = kwargs["S"] * (1 - (t[rel_select] - rel_min) / (rel_max - rel_min))

        return res



class Oscillator(Instrument):
    """

    Represents a basic oscillator, which is the base class for most synths

    """

    def __init__(self, waveform=chaudio.waves.sin, amp=1.0, amp_env=None, samplerate=None, phase_shift=0, freq_shift=0, tweak=None, pan=0, **kwargs):
        """Initializes an oscillator, given waveform and a host of other parameters

        
        Keep in all parameters can be overriden in individual calls to the :meth:`chaudio.instruments.Oscillator.note` function. So, to override the ``phase_shift`` for a single note, run like ``osc.note("A4", phase_shift=2) to temporarily override the initialized parameter.

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
        if amp_env is None:
            amp_env = ADSREnvelope()

        kwargs["waveform"] = waveform
        kwargs["amp"] = amp
        kwargs["amp_env"] = amp_env
        kwargs["samplerate"] = samplerate
        kwargs["phase_shift"] = phase_shift
        kwargs["freq_shift"] = freq_shift
        kwargs["tweak"] = tweak
        kwargs["pan"] = pan
        super(Oscillator, self).__init__(**kwargs)

    def __str__(self):
        return "Oscillator (%s)" % ", ".join([k + "=" + (self.kwargs[k].__name__ if hasattr(self.kwargs[k], "__name__") else str(self.kwargs[k])) for k in self.kwargs])

    __repr__ = __str__

    def raw_note(self, **kwargs):
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
        amp_env = kwargs["amp_env"]
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
            data[key] = amp_env.calc_val(t) * amp * waveform(t + phase_shift[key] / freq[key], freq[key], tweak=tweak[key])

        res = chaudio.source.Stereo(((1 - adj_pan) * data["left"], adj_pan * data["right"]), samplerate)

        return res


class MultiOscillator(Instrument):
    """

    Similar to LMMS's triple oscillator (which itself was based on minimoog synth), but with a variable number

    """

    def __init__(self, osc, **kwargs):
        """Returns an instrument multiplexor with oscillators


        Parameters
        ----------
        osc : list, tuple, None
            The group of oscillators. These are all the oscillators that are played each time you ask for a note. You can change oscillators after construction using the :meth:`chaudio.instruments.MultiOscillator.add_osc` and :meth:`chaudio.instruments.MultiOscillator.remove_osc` methods.

        kwargs : (key word args)
            These are all values that can override the default values (which all are documented in the :meth:`chaudio.instruments.Oscillator.__init__` method). 

        Returns
        -------

        :class:`chaudio.instruments.MultiOscillator`
            The multioscillator representing the oscillators playing the note

        """
        if osc is None:
            osc = []

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

    def raw_note(self, **kwargs):
        kwargs = self.merged_kwargs(kwargs)

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


presets = { }

presets["sin"] = Oscillator(waveform=chaudio.waves.sin)
presets["square"] = Oscillator(waveform=chaudio.waves.square)
presets["saw"] = Oscillator(waveform=chaudio.waves.saw)
presets["triangle"] = Oscillator(waveform=chaudio.waves.triangle)

presets["bass"] = MultiOscillator([])

presets["bass"].add_osc(Oscillator(waveform=chaudio.waves.square, samplerate=None, phase_shift=.4, freq_shift=(-1210, -1199), tweak=.4, pan=-.6, amp=.55, amp_env=ADSREnvelope(A=.25, D=0, S=1, R=.1)))
presets["bass"].add_osc(Oscillator(waveform=chaudio.waves.triangle, samplerate=None, phase_shift=.7, freq_shift=(-513, -496), tweak=(.2, .28), pan=.4, amp=.25, amp_env=ADSREnvelope(A=.4, D=.6, S=.75, R=.2)))



