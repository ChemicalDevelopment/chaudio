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

# how many measures to copy
measures = 4

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
bass = chaudio.fromfile(chaudio.samples["bass.wav"]) * 1.35
snare = chaudio.fromfile(chaudio.samples["snare.wav"]) * 1.3

hat = {
    "opened": chaudio.fromfile(chaudio.samples["hat_opened.wav"]) * .4,
    "closed": chaudio.fromfile(chaudio.samples["hat_closed.wav"]) * .4
}

# set up the beat
for b in range(0, tsig.top):
    beat[0, b] = bass

for b in range(0, 2):
    beat[0, b * 4 + 1] = snare
    beat[0, b * 4 + 1.5] = snare
    beat[0, b * 4 + 3] = snare

for b in range(0, tsig.top * 2):
    fv = b / 2.0
    if b in (7, 13, 15):
        beat[0, fv] = hat["opened"]
    else:
        beat[0, fv] = hat["closed"]
    
# bassline is all in sin waves
wave = wf.sin

# returns time array of so many beats
t = lambda beats: times(tsig[0, beats])

# chords from `lizardcrats`
bassline[0, 0] = wave(t(3), note("A3"))
bassline[0, 3] = wave(t(1), note("C3"))
bassline[0, 4] = wave(t(2), note("G2"))
bassline[0, 6] = wave(t(2), note("D3"))

wave = wf.triangle

# melody from `lizardcrats`
melody[0, 1] = wave(t(.5), note("G3"))
melody[0, 1.5] = wave(t(1), note("D3"))
melody[0, 2.5] = wave(t(.5), note("D3"))
melody[0, 3] = wave(t(1), note("E3"))

melody[0, 5.5] = wave(t(.5), note("G3"))
melody[0, 6] = wave(t(.5), note("D3"))
melody[0, 6.5] = wave(t(.5), note("D3"))
melody[0, 7] = wave(t(.5), note("E3"))
melody[0, 7.5] = wave(t(.5), note("G3"))

# insert all parts into final arranger
for i in range(0, measures):
    y[i, 0] = beat
    y[i, 0] = bassline
    y[i, 0] = melody


# export to file
chaudio.tofile("composed.wav", y)

