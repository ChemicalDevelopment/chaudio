"""

simple example usage of chaudio

"""

import chaudio

#chaudio.defaults["hz"] = 384000

# create our array of time samples (lasting 5 seconds)
t = chaudio.times(5)

inst = chaudio.instruments.presets["lead"]

# our air pressure array
y = inst.note(freq=440, t=8)

# outputs the sound to `simple.wav` using default settings
chaudio.tofile("instrument.wav", y)
#chaudio.play(y)
