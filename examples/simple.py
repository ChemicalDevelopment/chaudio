"""

simple example usage of chaudio

"""

import chaudio

# create our array of time samples (lasting 10 seconds)
t = chaudio.times(5)

# our air pressure
y = chaudio.waveforms.sin(t, chaudio.note("A4"))

# outputs the sound to `simple.wav` using default settings
chaudio.tofile("simple.wav", y)

