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
from chaudio import (TimeSignature, Track)
from chaudio.plugins import (Fade, Echo, Butter, Volume)
from chaudio.arrangers import ExtendedArranger

# tempo, in bpm
tempo = 114

# how many times to repeat the bar
repeats = 4

chaudio.defaults["timesignature"] = TimeSignature(4, 4, tempo)


# our tracks, act as compositions/sheet music
bassline = Track()
melody = Track()
beat = Track()

# add_note accept (offset, freq, length)
# where offset is (measures, beats)
# freq is a hz value, or a string note
# and length is either beats or (measures, beats)
bassline.add_note((0, 0), "A3", 3)
bassline.add_note((0, 3), "C3", 1)
bassline.add_note((1, 0), "G2", 2)
bassline.add_note((1, 2), "D2", 2)

melody.add_note((0, 1), "G3", .5)
melody.add_note((0, 1.5), "D3", 1)
melody.add_note((0, 2.5), "D3", .5)
melody.add_note((0, 3), "E3", 1)

melody.add_note((1, 1.5), "G3", .5)
melody.add_note((1, 2), "D3", .5)
melody.add_note((1, 2.5), "D3", .5)
melody.add_note((1, 3), "E3", .5)
melody.add_note((1, 3.5), "G3", .5)


# now set up the beat
for b in range(0, 8):
    # bass drum
    beat.add_note(b, key="bass")

    # snares
    if b % 2 == 1:
        beat.add_note(b, key="snare")
    if b % 4 == 1:
        beat.add_note(b+.5, key="snare", amp=.6)

    # hats
    beat.add_note(b, key="hat_closed")

    if b % 2 == 1 and b > 1:
        beat.add_note(b + .5, key="hat_opened")
    else:
        beat.add_note(b + .5, key="hat_closed")


# now for the actual combining

# our final arranger, which the other three will be inserted into
y = ExtendedArranger(setitem="beat")

bassline_instrument = chaudio.instruments.presets["bass"]
melody_instrument = chaudio.instruments.presets["lead"]

beat_instrument = chaudio.instruments.MultiSampler()

beat_instrument["bass"] = chaudio.instruments.Sampler(source=chaudio.samples["bass.wav"])
beat_instrument["snare"] = chaudio.instruments.Sampler(source=chaudio.samples["snare.wav"])
beat_instrument["hat_opened"] = chaudio.instruments.Sampler(source=chaudio.samples["hat_opened.wav"] * .3)
beat_instrument["hat_closed"] = chaudio.instruments.Sampler(source=chaudio.samples["hat_closed.wav"] * .4)


# insert all parts into final arranger, however many times are specified (by default, 4)
for i in range(0, repeats):
    y[2 * i, 0] = bassline.play(bassline_instrument)
    y[2 * i, 0] = melody.play(melody_instrument)
    y[2 * i, 0] = beat.play(beat_instrument)


# export to file, and then play it through speakers

#chaudio.tofile("arranged.wav", y)
chaudio.play(y)


# you can just output the bassline, for example
#chaudio.tofile("arranged_bassline.wav", bassline.play(bassline_instrument))

# cool audio effects when it is low quality
#chaudio.tofile("arranged_8i.wav", y, "8i")


