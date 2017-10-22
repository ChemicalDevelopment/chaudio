"""

simple example usage of chaudio

"""

import chaudio
#import viewer
import waveforms as wf
import freq


# create our array of time samples (lasting 4 seconds)
t = chaudio.times(1)

# our air pressure array, combining a low square wave and a high triangle wave
y = .5 * wf.square(t, freq.A3) + 5 * wf.triangle(t, freq.E5)

# open a window showing a graph of the samples
#viewer.show_data(y)

# open a window showing a graph of frequency-volume correlation
#viewer.show_frequency_graph(y)


# outputs the sound to `simple.wav` using default settings
chaudio.tofile("simple.wav", y)


#input("press enter to close")

