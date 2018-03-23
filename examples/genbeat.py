"""

generate a trap beat

"""
import chaudio
from chaudio import instruments

#t = chaudio.times(5)


def gen_kicks():

    inst = instruments.Oscillator()
    
    inst.add_plugin(chaudio.plugins.fade.Fade(sec=0.15, fadein=False, fadeout=True))
    inst.add_plugin(chaudio.plugins.filters.Butter(cutoff=1800, btype="lowpass", order=5))


    waves = (chaudio.waves.sin, chaudio.waves.square)
    freq_shifts = (-3600, -2400)
    predelays = (.006, .012)
    decays = (.01, .0008)
    t_decays = (.35, .1, .001)
    
    
    num_files = 0
    for wave in waves:
        inst["waveform"] = wave
        for freq_shift in freq_shifts:
            inst["freq_shift"] = freq_shift
            for predelay in predelays:
                for decay in decays:
                    inst["amp_env"] = instruments.ExponentialDecayEnvelope(predelay=predelay, decay=decay)
                    for t_decay in t_decays:
                        inst["freq_env"] = instruments.Pitch808Envelope(s_off=2400, t_decay=t_decay)

                        file_name = "kick_chaudio_%2d" % num_files

                        chaudio.tofile("RAW_OUTPUT/kicks/%s.wav" % file_name, chaudio.util.normalize(inst.note(freq=220, t=1.0)) * 0.8, normalize=False)

                        num_files += 1

    #y = inst.note(freq=220, t=1)

    #chaudio.play(y)

def gen_808s():
    tweaks = (None, 0.18, 0.9)

    waves = (chaudio.waves.square, chaudio.waves.triangle)

    amp_envs = (instruments.ExponentialDecayEnvelope(predelay=1.5, decay=.82), instruments.ExponentialDecayEnvelope(predelay=.4, decay=.34), instruments.ExponentialDecayEnvelope(predelay=0.0, decay=1.0))

    freq_envs = (instruments.Pitch808Envelope(s_off=1200, t_decay=.06, predelay=0.06), instruments.Pitch808Envelope(s_off=1800, t_decay=.12, predelay=.06))

    #inst = chaudio.instruments.presets["trap_bass"]
    inst = instruments.Oscillator(freq_shift=-3600)

    inst.add_plugin(chaudio.plugins.filters.Butter(cutoff=1400, btype="lowpass", order=5))

    #inst.add_plugin(chaudio.plugins.fade.Fade(sec=0.01, fadein=True, fadeout=False))
    inst.add_plugin(chaudio.plugins.fade.Fade(sec=0.15, fadein=False, fadeout=True))


    num_files = 0

    for wave in waves:
        inst["waveform"] = wave
        for tweak in tweaks:
            inst["tweak"] = tweak
            for amp_env in amp_envs:
                inst["amp_env"] = amp_env
                for freq_env in freq_envs:
                    inst["freq_env"] = freq_env


                    fname = "808_chaudio_%03d.wav" % num_files
                    chaudio.tofile("RAW_OUTPUT/808s/%s" % fname, chaudio.util.normalize(inst.note(freq=220, t=10)) * 0.8, normalize=False)
                    num_files += 1


gen_808s()
#gen_kicks()

"""
track = chaudio.track.Track(timesignature=chaudio.TimeSignature(4, 4, 120))
track.add_note((0, 0), "C3", 2.25)
track.add_note((0, 3), "C3", .3)
track.add_note((0, 3.33), "C3", .3)
track.add_note((0, 3.66), "C3", .3)
track.add_note((1, 0), "C3", 1.5)
track.add_note((1, 2.5), "C3", .5)
track.add_note((1, 3.0), "C3", .5)
track.add_note((2, 0), "E3", .5)
track.add_note((2, .5), "C3", .5)
track.add_note((2, 1), "C4", .3)
track.add_note((2, 1.33), "G3", .3)
track.add_note((2, 1.66), "G3", .3)
y = track.play(inst)
"""

# our air pressure array
#y = inst.note(freq=220, t=10) * 1.2



# outputs the sound to `simple.wav` using default settings

#chaudio.play(y)
#chaudio.tofile("808_chaudio.wav", y, normalize=False)
