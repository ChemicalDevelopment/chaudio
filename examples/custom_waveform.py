"""

generate a trap beat

"""
import chaudio
from chaudio import instruments


#waveform = "./chaudio/samples/waveforms/wv_2.wav"
#waveform = "./n_wv.wav"

#inst = instruments.Oscillator(waveform=chaudio.waves.get_sample_wave(chaudio.fromfile(waveform)))
inst = instruments.Oscillator(waveform=chaudio.waves.triangle)

#inst.add_plugin(chaudio.plugins.filters.Butter(btype="lowpass", cutoff=4000))
inst.add_plugin(chaudio.plugins.filters.Butter(btype="lowpass", cutoff=600))

inst["freq_env"] = instruments.Pitch808Envelope(s_off=800, t_decay=.08, predelay=0.025)
inst["amp_env"] = instruments.ExponentialDecayEnvelope(predelay=2.5, decay=.96)


# our air pressure array
y = inst.note(freq="A0", t=10)
chaudio.play(y)


# outputs the sound to `simple.wav` using default settings

#chaudio.play(y)
chaudio.tofile("custom_wav_out.wav", y)
