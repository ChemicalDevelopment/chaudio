Getting Started
===============

Once you've installed chaudio, you will want to start making music.

First, in either python2 or python3, you can run:

::

    import chaudio

And now you have access to all of the chaudio library


First, we'll start with generating a simple note:

::


    # create our array of time samples (lasting 5 seconds)
    t = chaudio.times(5)

The ``chaudio.times`` function returns an array of times at which audio samples are to be created, for 5 seconds of data. By default, the samplerate (also referred to as `hz`, or samples per second) is 44100, which is the most common value.


::


    pitch = chaudio.note("A3")

The ``chaudio.note`` function returns a pitch (in `hz`) of the desired note and octave. For example, ``chaudio.note("A3") == 220.0``

::


    # our air pressure array, generated using a square wave
    y = chaudio.waves.square(t, pitch)

The ``chaudio.waves.square`` is a waveform function, that is, it takes time sample values, and a frequency, and returns a signal representing that (in this case, the form of this function is called a `square wave <https://en.wikipedia.org/wiki/Square_wave>`_). Each waveform has its own timbre (pronounced `TAM-BER`), which we will cover in a future section.

Now, we use our sample times, ``t``, and our note pitch ``pitch``, feed that through our waveform generator, ``chaudio.waves.square``, which returns an array of pressure values. And, viola, we have the data representing an `A3` played on a square oscillator. But, how do we hear it?

::

    chaudio.tofile("~/Music/square_A3.wav", y)

The function ``chaudio.tofile`` takes either a filename, or file pointer object, and then a data array of samples. It does all neccessary conversions, and now, just open up your music folder ``~/Music``, and open ``square_A3.wav``. You should hear the square wave playing the `A3` note.


So, all together, this example can be ran as such:

::

    import chaudio

    t = chaudio.times(5)

    pitch = chaudio.note("A3")

    y = chaudio.waves.square(t, pitch)

    chaudio.tofile("~/Music/square_A3.wav", y)

