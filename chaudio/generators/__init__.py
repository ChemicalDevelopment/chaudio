"""Generators (:mod:`chaudio.generators`)
==============================================

.. currentmodule:: chaudio.generators


Basically track generation routines for common genres

"""

import chaudio
import random
import math
import numpy as np


def pop_bassline(measures=4, base=None, tsig=None):
    if not base:
        base = random.choice(list(chaudio.util.valid_note_names.keys())) + "3"
    if not tsig:
        tsig = chaudio.defaults["timesignature"]

    ret = chaudio.Track(timesignature=tsig)

    prog = "I-IV-V-IV"
    chords = chaudio.util.chords.progression(base, prog)

    for m in range(0, measures):
        cchord = chords[m % len(chords)]

        cchord += cchord[0] + 12

        notes = cchord.get_notes()

        ret.add_note((m, 0), notes[0], tsig.beats)
        cchord_jumbled = np.random.permutation(notes[1:])

        for b in range(1, tsig.beats):
            ret.add_note((m, b), cchord_jumbled[(b - 1) % len(cchord_jumbled)], 1, amp=1.0 / (math.sqrt(b + 1) + .5))

    return ret