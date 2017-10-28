"""

simple example usage of chaudio

"""

import chaudio

# create our array of time samples (lasting 5 seconds)
t = chaudio.times(5)

# our air pressure array
y = chaudio.waves.square(t, chaudio.note("A3"))

# outputs the sound to `simple.wav` using default settings
chaudio.tofile("simple.wav", y)
