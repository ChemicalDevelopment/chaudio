"""

All things graphing, like an oscilliscope, etc

"""


import chaudio

import numpy as np
import matplotlib.pyplot as plt

#plt.ion()


def show_raw(x, y, title="graph", xlabel=None, ylabel=None):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.plot(x, y)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

# shows basic sample data
def show_data(samples):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.plot(samples)

    ax.set_title("Air Pressure")
    ax.set_xlabel("Sample")
    ax.set_ylabel("Sample Value")

    #plt.draw()

def show_frequency_graph(samples, N=None, samplerate=44100, maxfreq=44100):
    if N is None:
        N = samplerate

    fftdata = np.abs(np.fft.fft(samples, N)[:N//2]) * (2.0 / N)
    fftfreq = np.fft.fftfreq(N)[:N//2] * samplerate

    num_to_show = 0
    for i in fftfreq:
        if i <= maxfreq:
            num_to_show += 1
        else:
            break

    fftfreq = fftfreq[:num_to_show+1]
    fftdata = fftdata[:num_to_show+1]

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.plot(fftfreq, fftdata, marker='x')
    ax.set_title("Frequency Volumes")
    ax.set_xlabel("Frequency ($hz$)")
    ax.set_ylabel("Volume")

def show():
    plt.show()



