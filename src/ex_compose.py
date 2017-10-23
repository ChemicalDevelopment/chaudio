"""

how to use AudioSource 's to compose and string together audio

"""

import chaudio
from chaudio import times
import waveforms as wf
import freq
import plugins

# create our array of time samples (lasting 10 seconds)
t = times(.2)

# our air pressure array, combining a low square wave and a high triangle wave
y = chaudio.SmoothedSignalAudioSource()

raw = chaudio.BasicAudioSource()

# some plugins we will use
low_noise = plugins.NoisePlugin(amp=.1)
high_noise = plugins.NoisePlugin(amp=1.5)



print ("created audio source")

beat = 60.0 / 120.0
#raw.insert_time(wf.square(times(5 * beat), freq.C2), 0)

y.insert_time(raw, 0)

raw.insert_time(wf.square(times(5 * beat), freq.C7), 0)

#y.ensure_updated_final_data()

#y.insert_time(wf.triangle(times(3 * beat), freq.A4), 0)
#y.insert_time(wf.triangle(times(1 * beat), freq.C5), 3 * beat)
#y.insert_time(wf.triangle(times(2 * beat), freq.G4), 4 * beat)
#y.insert_time(wf.triangle(times(2 * beat), freq.D5), 6 * beat)

#y.insert_time(wf.triangle(t, freq.A4), 0)
#y.insert_time(wf.triangle(t, freq.A4), 0)
#y.insert_time(wf.triangle(t, freq.A5), 3.0)
#y.insert_time(wf.triangle(t, freq.F4), 4.0)
#y.insert_time(wf.triangle(t, freq.E6), 5.0)

#y.insert_time(wf.saw(t, freq.C5), 2.5)
#y.insert_time(wf.saw(t, freq.E5), 3.5)
#y.insert_time(wf.triangle(t, freq.A5), 5.0)

print ("calculated notes to be played")

print ("outputting now")
#y.add_final_plugin(plugins.EchoPlugin(delay=int(44100//3.5)))
# outputs the simple smoothed audio source to the basic wave
chaudio.tofile("composed_echo.wav", y)

# introduce some low noise
#y.add_final_plugin(low_noise)
#chaudio.tofile("composed_low_noise.wav", y)

# remove low noise, add in louder noise
#y.remove_final_plugin(low_noise)
#y.add_final_plugin(high_noise)
#chaudio.tofile("composed_high_noise.wav", y)

