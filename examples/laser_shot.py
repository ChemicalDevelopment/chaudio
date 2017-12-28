"""

simple example usage of chaudio to create a laser shot sound effect

"""

import chaudio

# create our array of time samples (lasting .35 seconds)
t = chaudio.times(.35)

# calculate the frequencies
thz = chaudio.util.glissando_freq("A7", "A0", t)

# pick an instrument (this is a good one for laser shot)
inst = chaudio.instruments.presets["lead"]

# play the note, capture the result
y = inst.note(freq=thz, t=t)

# store it, or play it through speakers
chaudio.tofile("laser_shot.wav", y)
#chaudio.play(y)


