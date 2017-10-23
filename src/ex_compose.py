"""

how to use AudioSource 's to compose and string together audio

"""

import chaudio
from chaudio import times

import waveforms as wf

import freq
from freq import note

import plugins
import arrangers

# create our array of time samples (lasting 10 seconds)

timesignature = chaudio.TimeSignature(4, 4, 120)

freq.note("A#3")

y = arrangers.ExtendedArranger(setitem="beat", timesignature=timesignature)

noise = plugins.Noise(amp=.05)
fade = plugins.Fade()
echo = plugins.Echo(amp=.5, delay=44100//1.2, decay=.4, num=12)

#y.add_insert_plugin(noise)
y.add_insert_plugin(fade)
#y.add_insert_plugin(echo)

n1 = times(timesignature[0, 1])
n2 = times(timesignature[0, 2])
n3 = times(timesignature[0, 3])

# [a, b] represents a'th measure and b'th beat (from our timesignautre we created y with)
y[0, 0] = wf.square(n3, note("A2"))
y[0, 3] = wf.square(n1, note("C2"))
y[1, 0] = wf.square(n2, note("G1"))
y[1, 2] = wf.square(n2, note("D2"))

chaudio.tofile("composed.wav", y)


