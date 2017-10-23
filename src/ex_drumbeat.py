"""


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

y = arrangers.ExtendedArranger(setitem="beat", timesignature=timesignature)
beat = arrangers.ExtendedArranger(setitem="beat", timesignature=timesignature)

fade = plugins.Fade()
#echo = plugins.Echo(amp=.4, delay=44100//3.8, decay=.86, num=20)
#butter0 = plugins.ButterFilter(cutoff=100, btype="highpass")
#butter1 = plugins.ButterFilter(cutoff=20000, btype="lowpass")
#pitchshift = plugins.PitchShift(cents=1200)

#y.add_insert_plugin(fade)
#y.add_insert_plugin(echo)
#y.add_insert_plugin(noise)

bass = chaudio.fromfile("samples/bass.wav", combine=True)
snare = chaudio.fromfile("samples/snare.wav", combine=True)
hat = {
    "closed": chaudio.fromfile("samples/hat_closed.wav", combine=True) * .2,
    "opened": chaudio.fromfile("samples/hat_opened.wav", combine=True) * .2
}


beat[0, 0] = hat["closed"]
beat[0, .5] = hat["closed"]
beat[0, 1] = hat["opened"]
beat[0, 1.5] = hat["closed"]
beat[0, 2] = hat["closed"]
beat[0, 2.5] = hat["closed"]
beat[0, 3] = hat["opened"]
beat[0, 3.5] = hat["closed"]

beat[1, 0] = hat["closed"]
beat[1, .5] = hat["closed"]
beat[1, 1] = hat["opened"]
beat[1, 1.5] = hat["closed"]
beat[1, 2] = hat["opened"]
beat[1, 2.25] = hat["opened"]
beat[1, 2.5] = hat["opened"]
beat[1, 2.75] = hat["opened"]
beat[1, 3] = hat["opened"]
beat[1, 3.25] = hat["opened"]
beat[1, 3.5] = hat["opened"]
beat[1, 3.75] = hat["opened"]


beat[0, 0] = bass

beat[0, 1] = snare
beat[0, 2] = bass
beat[0, 2.5] = bass
beat[0, 3] = snare

beat[1, 0] = bass
beat[1, 1] = snare
beat[1, 2] = snare
beat[1, 2.25] = snare
beat[1, 2.5] = snare
beat[1, 2.75] = snare
beat[1, 3] = snare
beat[1, 3.25] = snare
beat[1, 3.5] = snare
beat[1, 3.75] = snare

y[0, 0] = beat
y[2, 0] = beat
y[4, 0] = beat
y[6, 0] = beat


chaudio.tofile("beat.wav", y)


