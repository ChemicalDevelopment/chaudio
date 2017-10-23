"""

simple example usage of chaudio

"""

import chaudio
import waveforms as wf
import freq


# create our array of time samples (lasting 10 seconds)
t = chaudio.times(10)

# our air pressure array, combining a low square wave and a high triangle wave
y = .5 * wf.square(t, freq.A3) + 5 * wf.triangle(t, freq.E5)

# outputs the sound to `simple.wav` using default settings
chaudio.tofile("simple.wav", y)


