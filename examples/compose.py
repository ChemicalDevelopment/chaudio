"""

how to use Arranger 's and samples to create a song (`lizardcrats`)

"""

import chaudio

import chaudio.waveforms as wf

from chaudio import (times, note)
from chaudio.plugins import (Fade, Echo, ButterFilter)
from chaudio.arrangers import ExtendedArranger

# time signature (8/4, 120 bpm)
tsig = chaudio.TimeSignature(8, 4, 120)

# our arrangers, which take in samples and signals
beat = ExtendedArranger(setitem="beat", timesignature=tsig)
bassline = ExtendedArranger(setitem="beat", timesignature=tsig)
melody = ExtendedArranger(setitem="beat", timesignature=tsig)
y = ExtendedArranger(setitem="beat", timesignature=tsig)

# plugins
fade = Fade()
echo = Echo(amp=.6, delay=44100//3.6, decay=.5, num=12)

# butterworth plugin filters, these remove artifacts
butter0 = ButterFilter(cutoff=100, btype="highpass")
butter1 = ButterFilter(cutoff=18000, btype="lowpass")


# don't add any filters to the beat, because those are drum samples, and should not be changed in any way

# the baseline should echo, in addition to everything the melody does
bassline.add_insert_plugin(fade)
bassline.add_insert_plugin(echo)
bassline.add_final_plugin(butter0)
bassline.add_final_plugin(butter1)

melody.add_insert_plugin(fade)
melody.add_final_plugin(butter0)
melody.add_final_plugin(butter1)


# read in drum samples
bass = chaudio.fromfile("samples/bass.wav") * 1.35
snare = chaudio.fromfile("samples/snare.wav") * 1.3

hat = {
    "opened": chaudio.fromfile("samples/hat_opened.wav") * .4,
    "closed": chaudio.fromfile("samples/hat_closed.wav") * .4
}

# set up the beat
beat[0, 0] = bass
beat[0, 1] = bass
beat[0, 2] = bass
beat[0, 3] = bass
beat[0, 4] = bass
beat[0, 5] = bass
beat[0, 6] = bass
beat[0, 7] = bass

beat[0, 1] = snare
beat[0, 1.5] = snare
beat[0, 3] = snare

beat[0, 5] = snare
beat[0, 5.5] = snare
beat[0, 7] = snare

beat[0, 0] = hat["closed"]
beat[0, 0.5] = hat["closed"]
beat[0, 1] = hat["closed"]
beat[0, 1.5] = hat["closed"]
beat[0, 2] = hat["closed"]
beat[0, 2.5] = hat["closed"]
beat[0, 3] = hat["closed"]
beat[0, 3.5] = hat["opened"]
beat[0, 4] = hat["closed"]
beat[0, 4.5] = hat["closed"]
beat[0, 5] = hat["closed"]
beat[0, 5.5] = hat["closed"]
beat[0, 6] = hat["closed"]
beat[0, 6.5] = hat["opened"]
beat[0, 7] = hat["closed"]
beat[0, 7.5] = hat["opened"]

# bassline is all in sin waves
wave = wf.sin

# notes that are .5, 1, 2 and 3 beats respectively
th = times(tsig[0, 0.5])
t1 = times(tsig[0, 1])
t2 = times(tsig[0, 2])
t3 = times(tsig[0, 3])

# chords from `lizardcrats`
bassline[0, 0] = wave(t3, note("A3"))
bassline[0, 3] = wave(t1, note("C3"))
bassline[0, 4] = wave(t2, note("G2"))
bassline[0, 6] = wave(t2, note("D3"))

wave = wf.triangle

# melody from `lizardcrats`
melody[0, 1] = wave(th, note("G3"))
melody[0, 1.5] = wave(t1, note("D3"))
melody[0, 2.5] = wave(th, note("D3"))
melody[0, 3] = wave(t1, note("E3"))

melody[0, 5.5] = wave(th, note("G3"))
melody[0, 6] = wave(th, note("D3"))
melody[0, 6.5] = wave(th, note("D3"))
melody[0, 7] = wave(th, note("E3"))
melody[0, 7.5] = wave(th, note("G3"))

bassline.kwargs["name"] = "bassline"

# insert all parts into final arranger

y[0, 0] = bassline
y[1, 0] = bassline
y[2, 0] = bassline
y[3, 0] = bassline

y[0, 0] = melody
y[1, 0] = melody
y[2, 0] = melody
y[3, 0] = melody


y[0, 0] = beat
y[1, 0] = beat
y[2, 0] = beat
y[3, 0] = beat

# export to file
chaudio.tofile("composed.wav", y)

