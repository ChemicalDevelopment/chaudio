"""

creating a song (inspired by Lizardcrats) using the more advanced parts of the library (plugins, arrangers)

essentially, the function of an arranger is to:
  - combine other arrangers and sources, essentially the main functionality of chaudio
  - record each operation, and recalculate the result if any source changes

the recalculation occurs if:
  - a new source/arranger is inserted
  - a new plugin is added

a plugin can be applied as a 'insert' plugin (which is ran on audio as it is inserted), or a 'final' plugin (which are ran on the result of all insert plugins)


"""

import chaudio

from chaudio import (times, note)
from chaudio.plugins import (Fade, Echo, Butter, Volume)
from chaudio.arrangers import ExtendedArranger

# time signature (8/4, 120 bpm)
tsig = chaudio.TimeSignature(8, 4, 120)

# how many times to repeat the bar
measures = 4

# our arrangers, which take in sources, as well as other arrangers
beat = ExtendedArranger(setitem="beat", timesignature=tsig)
bassline = ExtendedArranger(setitem="beat", timesignature=tsig)
melody = ExtendedArranger(setitem="beat", timesignature=tsig)

# our final arranger, which the other three will be inserted into
y = ExtendedArranger(setitem="beat", timesignature=tsig)


# plugins to use
fade = Fade()
echo = Echo(amp=.7, idelay=1.0/8, delay=1.0/4, decay=.76, num=20)

# butterworth plugin filters, these remove extremely low and high frequencies
butter0 = Butter(cutoff=20000, btype="lowpass")
butter1 = Butter(cutoff=30, btype="highpass")


# don't add any filters to the beat, because they are samples

# the baseline should echo, and needs to be louder
bassline.add_insert_plugin(fade)
bassline.add_insert_plugin(echo)
bassline.add_final_plugin(Volume(amp=8))

melody.add_insert_plugin(fade)
melody.add_final_plugin(Volume(amp=1.8))

beat.add_final_plugin(Volume(amp=.8))


# this will affect all things in the arranger (including drum samples), so the cutoffs have to not remove crucial information (20000 and 30 are pretty good values)
y.add_final_plugin(butter0)
y.add_final_plugin(butter1)


# read in drum samples
bass = chaudio.samples["bass.wav"] * .95
snare = chaudio.samples["snare.wav"] * .9

hat = {
    "opened": chaudio.samples["hat_opened.wav"] * .2,
    "closed": chaudio.samples["hat_closed.wav"] * .2
}

# set up the beat (assume the beat is one measure, so all should be like beat[0, X], using 0)

# bass hit every beat
for b in range(0, tsig.beats):
    beat[0, b] = bass

# snare hit on off beats (1, 3, 5, 7)
for b in range(1, tsig.beats, 2):
    beat[0, b] = snare
    # on beats 1 and 5, a second snare hit happens a quarter note after, but slightly softer
    if b % 4 == 1:
        beat[0, b + .5] = snare * .72

# the hat is going twice per beat, with some open samples
for b in range(0, tsig.beats):
    beat[0, b] = hat["closed"]
    # on these beats, the second hat should be opened
    if b in (3, 5, 7):
        beat[0, b + .5] = hat["opened"]
    else:
        beat[0, b + .5] = hat["closed"]


# bassline is all in sin waves
wave = chaudio.waves.sin

# returns time array of so many beats
t = lambda beats: times(tsig[0, beats])

# notes from Lizardcrats
# the bass time should only be .25 beats, because echo is applied. we want the main sound to end
bt = t(.2)
bassline[0, 0] = wave(bt, note("A3"))
bassline[0, 3] = wave(bt, note("C3"))
bassline[0, 4] = wave(bt, note("G2"))
bassline[0, 6] = wave(bt, note("D2"))


# triangle wave for the melody
wave = chaudio.waves.triangle

# melody from Lizardcrats
melody[0, 1] = wave(t(.5), note("G3"))
melody[0, 1.5] = wave(t(1), note("D3"))
melody[0, 2.5] = wave(t(.5), note("D3"))
melody[0, 3] = wave(t(1), note("E3"))

melody[0, 5.5] = wave(t(.5), note("G3"))
melody[0, 6] = wave(t(.5), note("D3"))
melody[0, 6.5] = wave(t(.5), note("D3"))
melody[0, 7] = wave(t(.5), note("E3"))
melody[0, 7.5] = wave(t(.5), note("G3"))

# insert all parts into final arranger, however many times are specified (by default, 4)
for i in range(0, measures):
    y[i, 0] = beat
    y[i, 0] = bassline
    y[i, 0] = melody


chaudio.tofile("arranged.wav", y)
chaudio.play(y)


# export to file
#chaudio.tofile("composed.wav", wave(t(.5), note("G3")))

# you can just output the bassline, for example
#chaudio.tofile("composed_bassline.wav", bassline)

# cool audio effects when it is low poly
#chaudio.tofile("composed_8i.wav", y, "8i")


