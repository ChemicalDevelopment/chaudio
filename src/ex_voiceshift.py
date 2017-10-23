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

y = arrangers.ExtendedArranger(setitem="beat", timesignature=timesignature)
harmony1 = arrangers.ExtendedArranger(setitem="beat", timesignature=timesignature)
harmony2 = arrangers.ExtendedArranger(setitem="beat", timesignature=timesignature)

echo = plugins.Echo(amp=.4, delay=44100//3.8, decay=.86, num=20)
butter0 = plugins.ButterFilter(cutoff=200, btype="highpass")
butter1 = plugins.ButterFilter(cutoff=1000, btype="lowpass")

#pitchshift_third = plugins.PitchShift(cents=0)
#pitchshift_fifth = plugins.PitchShift(cents=40)

#harmony1.add_insert_plugin(pitchshift_third)
#harmony2.add_insert_plugin(pitchshift_fifth)

voice = chaudio.fromfile("voice.wav", combine=True)
voicei = -1.0 * voice

#harmony1[0, 0] = voice
#harmony2[0, 0] = voice

y[0, 0] = voice
y[0, 0] = voicei
#y[0, 0] = harmony1
#y[0, 0] = harmony2

# y.add_final_plugin(butter0)
# y.add_final_plugin(butter1)

chaudio.tofile("voice_harmony.wav", y)


