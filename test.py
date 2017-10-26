

import chaudio


x = chaudio.Source((chaudio.waveforms.sin(chaudio.times(.00005), 440), chaudio.waveforms.saw(chaudio.times(.00005), 440)))

print (x[:][:])

x.hz = x.hz * 2

print (x[:][:])


x.hz = x.hz / 2

print (x[:][:])

