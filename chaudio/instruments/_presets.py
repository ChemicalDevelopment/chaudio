"""Instruments Presets (:mod:`chaudio.instruments._presets`)
==============================================

.. currentmodule:: chaudio.instruments._presets

Internal file for instrument presets. To access these, use the object ``chaudio.instruments.presets["KEY"]``.

"""

import chaudio
from chaudio import instruments

presets = { }

presets["sin"] = instruments.Oscillator(waveform=chaudio.waves.sin)
presets["square"] = instruments.Oscillator(waveform=chaudio.waves.square)
presets["saw"] = instruments.Oscillator(waveform=chaudio.waves.saw)
presets["triangle"] = instruments.Oscillator(waveform=chaudio.waves.triangle)

presets["bass"] = instruments.MultiOscillator([])

presets["bass"].add_osc(instruments.Oscillator(waveform=chaudio.waves.square, samplerate=None, phase_shift=.4, freq_shift=(-1203, -1193), tweak=.4, pan=-.6, amp=.55))
presets["bass"].add_osc(instruments.Oscillator(waveform=chaudio.waves.triangle, samplerate=None, phase_shift=.7, freq_shift=(-511, -496), tweak=(.2, .25), pan=.4, amp=.3))


"""

osc[0] = Oscillator(waveform=chaudio.waves.square, samplerate=None, phase_shift=.4, freq_shift=-1200, tweak=.4, pan=-.6, amp=.55)
osc[1] = Oscillator(waveform=chaudio.waves.triangle, samplerate=None, phase_shift=(.7, .5), freq_shift=(-508, -496), tweak=(.2, .45), pan=.4, amp=.3)
osc[2] = Oscillator(waveform=chaudio.waves.saw, samplerate=None, phase_shift=(.1, .15), freq_shift=(1918, 1890), tweak=(.28, .35), pan=-.2, amp=.15)

"""

