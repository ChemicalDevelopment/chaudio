"""

All things graphing, like an oscilliscope, etc

"""


import numpy as np
import matplotlib.pyplot as plt


import chaudio


plt.ion()



# shows basic sample data
def show_data(samples):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    print ("diff samples", )

    # used to determine line width
    diff_score = 4.0 / (1 + np.mean(np.diff(chaudio.normalize(samples))) * 10 ** 6.2)

    linewidth = diff_score

    ax.plot(samples, linewidth=linewidth)

    ax.set_title("Air Pressure")
    ax.set_xlabel("Sample")
    ax.set_ylabel("Sample Value")

    #plt.show()
    plt.draw()

def show_frequency_graph(samples, N=None, samplerate=44100):
    if N is None:
        N = samplerate

    fftdata = np.abs(np.fft.fft(samples, N)[:N//2]) * (2.0 / N)
    fftfreq = np.fft.fftfreq(N)[:N//2] * samplerate

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.plot(fftfreq, fftdata, marker='x')
    ax.set_title("Frequency Volumes")
    ax.set_xlabel("Frequency ($hz$)")
    ax.set_ylabel("Volume")
    #plt.show()
    plt.draw()




