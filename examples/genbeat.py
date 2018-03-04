"""

generate a trap beat

"""
import chaudio

t = chaudio.times(5)

inst = chaudio.instruments.presets["trap_bass"]

track = chaudio.track.Track(timesignature=chaudio.TimeSignature(4, 4, 120))
track.add_note((0, 0), "C3", 2.25)
track.add_note((0, 3), "E3", .3)
track.add_note((0, 3.33), "E3", .3)
track.add_note((0, 3.66), "E3", .3)
track.add_note((1, 0), "C3", 1.5)
track.add_note((1, 2.5), "C3", .5)
track.add_note((1, 3.0), "C3", .5)
track.add_note((2, 0), "E3", .5)
track.add_note((2, .5), "C3", .5)
track.add_note((2, 1), "C4", .3)
track.add_note((2, 1.33), "C4", .3)
track.add_note((2, 1.66), "C4", .3)


# our air pressure array
#y = inst.note(freq=440, t=8)

y = track.play(inst)


# outputs the sound to `simple.wav` using default settings

chaudio.play(y)

