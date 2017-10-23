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

timesignature = chaudio.TimeSignature(8, 4, 120)

beat = arrangers.ExtendedArranger(setitem="beat", timesignature=timesignature)
bassline = arrangers.ExtendedArranger(setitem="beat", timesignature=timesignature)
melody = arrangers.ExtendedArranger(setitem="beat", timesignature=timesignature)
y = arrangers.ExtendedArranger(setitem="beat", timesignature=timesignature)

fade = plugins.Fade()
echo = plugins.Echo(amp=.6, delay=44100//3.6, decay=.5, num=12)
butter0 = plugins.ButterFilter(cutoff=100, btype="highpass")
butter1 = plugins.ButterFilter(cutoff=10000, btype="lowpass")

bassline.add_final_plugin(butter0)
bassline.add_final_plugin(butter1)
bassline.add_insert_plugin(fade)
bassline.add_insert_plugin(echo)

melody.add_final_plugin(butter0)
melody.add_final_plugin(butter1)
melody.add_insert_plugin(fade)

bass = chaudio.fromfile("samples/bass.wav", combine=True) * 1.4
snare = chaudio.fromfile("samples/snare.wav", combine=True) * 1.25
hat = {
    "opened": chaudio.fromfile("samples/hat_opened.wav", combine=True) * .4,
    "closed": chaudio.fromfile("samples/hat_closed.wav", combine=True) * .4
}


beat[0, 0] = bass
beat[0, 1] = bass
beat[0, 2] = bass
beat[0, 3] = bass
beat[0, 4] = bass
beat[0, 5] = bass
beat[0, 6] = bass
beat[0, 7] = bass

beat[0, 1] = snare
beat[0, 1.5] = snare
beat[0, 3] = snare

beat[0, 5] = snare
beat[0, 5.5] = snare
beat[0, 7] = snare

beat[0, 0] = hat["closed"]
beat[0, 0.5] = hat["closed"]
beat[0, 1] = hat["closed"]
beat[0, 1.5] = hat["closed"]
beat[0, 2] = hat["closed"]
beat[0, 2.5] = hat["closed"]
beat[0, 3] = hat["closed"]
beat[0, 3.5] = hat["opened"]
beat[0, 4] = hat["closed"]
beat[0, 4.5] = hat["closed"]
beat[0, 5] = hat["closed"]
beat[0, 5.5] = hat["closed"]
beat[0, 6] = hat["closed"]
beat[0, 6.5] = hat["opened"]
beat[0, 7] = hat["closed"]
beat[0, 7.5] = hat["opened"]


wave = wf.sin
t3 = times(timesignature[0, 3])
t2 = times(timesignature[0, 2])
t1 = times(timesignature[0, 1])

bassline[0, 0] = wave(t3, freq.note("A3"))
bassline[0, 3] = wave(t1, freq.note("C3"))
bassline[0, 4] = wave(t2, freq.note("G2"))
bassline[0, 6] = wave(t2, freq.note("D3"))

wave = wf.triangle
tw = times(timesignature[0, 1.0])
th = times(timesignature[0, .5])

melody[0, 1] = wave(th, freq.note("G3"))
melody[0, 1.5] = wave(tw, freq.note("D3"))
melody[0, 2.5] = wave(th, freq.note("D3"))
melody[0, 3] = wave(tw, freq.note("E3"))

melody[0, 5.5] = wave(th, freq.note("G3"))
melody[0, 6] = wave(th, freq.note("D3"))
melody[0, 6.5] = wave(th, freq.note("D3"))
melody[0, 7] = wave(th, freq.note("E3"))
melody[0, 7.5] = wave(th, freq.note("G3"))

#melody.add_final_plugin(plugins.Volume(amp=.85))

y[0, 0] = bassline
y[1, 0] = bassline
y[2, 0] = bassline
y[3, 0] = bassline

y[0, 0] = melody
y[1, 0] = melody
y[2, 0] = melody
y[3, 0] = melody

y[0, 0] = beat
y[1, 0] = beat
y[2, 0] = beat
y[3, 0] = beat


chaudio.tofile("composed.wav", y)
chaudio.tofile("bassline.wav", bassline)


