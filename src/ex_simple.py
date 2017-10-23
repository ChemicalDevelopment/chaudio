"""

simple example usage of chaudio

"""

import chaudio
import waveforms as wf
import freq


# create our array of time samples (lasting 10 seconds)
t = chaudio.times(5)

# our air pressure array, combining a low square wave and a high triangle wave
#y = .5 * wf.square(t, freq.note("A3")) + 3 * wf.triangle(t, freq.note("E4"))

note = freq.note("A4")

y = wf.sin(t, note)

for i in range(2, 20):
    y += wf.sin(t, note * i) / i


# outputs the sound to `simple.wav` using default settings
chaudio.tofile("simple.wav", y)

chaudio.tofile("simple_saw.wav", wf.saw(t, note))


