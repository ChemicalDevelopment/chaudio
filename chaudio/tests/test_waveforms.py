"""

Source for generating waveforms (like sin, saw, square, etc)

In general, a function f should take in a time parameter `t` that can be either a normal float, or a numpy array, and `hz` should be able to be a constant or numpy array


"""


from unittest import TestCase

import chaudio
import numpy as np


class TestWave(TestCase):

    def test_basic(self):
        t = chaudio.times(1)
        y = chaudio.waves.sin(t, 1)
        self.assertTrue(np.sum(y ** 2) > 0.0)


