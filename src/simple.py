"""

simple example usage

"""

import chsound
#import viewer
import waveforms as wf
import freq as fq

t = chsound.times(10)

#y = waveforms.triangle(t, freq.A4) + waveforms.triangle(t, freq.E5)
Ey = sum([wf.triangle(t, i) for i in fq.chord(fq.A4, True)])

#viewer.show_data(y)

print ("to file")
chsound.tofile("triangle.wav", y)
print ('done')

