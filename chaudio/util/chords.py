"""Chord utilities

These are functions for chord generation

"""

from chaudio.util import transpose, note
import math


def first(base):
    return base

def second(base, minor=False):
    return transpose(base, 2 - minor, False)

def third(base, minor=False):
    return transpose(base, 4 - minor, False)

def fourth(base):
    return transpose(base, 5, False)

def tritone(base):
    return transpose(base, 6, False)

def fifth(base):
    return transpose(base, 7, False)

def sixth(base, minor=False):
    return transpose(base, 9 - minor, False)

def seventh(base, minor=False):
    return transpose(base, 11 - minor, False)

#def octave(base):
#    return transpose(base, 12, False)


class Chord(object):
    def __init__(self, notes, **kwargs):
        # notes should be in semitones
        if "transpose" not in kwargs:
            kwargs["transpose"] = 0
        self.notes = notes
        self.kwargs = kwargs

    def copy(self):
        return type(self)(notes=list(self.notes), **self.kwargs)

    def get_notes(self, root="A"):
        return [transpose(note(root), n + self.kwargs["transpose"], use_cents=False) for n in self.notes]
    
    def __getitem__(self, key):
        return self.notes.__getitem__(key)

    def invert(self, change=1):
        change = change % len(self.notes)
        self.notes = self.notes[-change:] + self.notes[:-change]

    def inverted(self, change=1):
        ret = self.copy()
        ret.invert(change)
        return ret

    def transpose(self, change):
        self.kwargs["transpose"] += change
    
    def transposed(self, change):
        ret = self.copy()
        ret.transpose(change)
        return ret

    def __str__(self):
        return "%s, %s, %s" % (type(self).__name__, self.kwargs, self.notes)

    def __len__(self):
        return self.notes.__len__()

    def __add__(self, val):
        if isinstance(val, str):
            return self.__add__(from_notation(val))
        if isinstance(val, int) or isinstance(val, float):
            r = self.copy()
            r.notes += [val]
            return r
        elif issubclass(type(val), Chord):
            r = self.copy()
            r.notes += [n + val.kwargs["transpose"] for n in val.notes]
            return r
        else:
            raise ValueError("Unknown type to add to chord, '%s'" % type(val).__name__)


class Triad(Chord):
    def __init__(self, **kwargs):
        if "minor" not in kwargs:
            kwargs["minor"] = False
        if "notes" in kwargs:
            pass
        #    raise Exception("Error: supplied notes in Triad class")
        kwargs["notes"] = [0, 4-kwargs["minor"], 7]
        super().__init__(**kwargs)

roman_numerals = {
    "i": 1,
    "ii": 2,
    "iii": 3,
    "iv": 4,
    "v": 5,
    "vi": 6,
    "vii": 7
}

# semitone offset for each chord
semitone_offsets = {
    1: 0,
    2: 2,
    3: 4,
    4: 5,
    5: 7,
    6: 9,
    7: 11,
}
    

def from_notation(notation):
    """

    notation should be like:

    (assumes C base)

    "I" C major

    "iii" E minor

    "biii" Eb minor

    "#III" E# (F) major

    "I7b" (dominant seventh)

    "I7" (major seventh)

    "i7" (minor seventh)

    """

    roman_numeral = ""
    rest = ""
    already_found_numeral = False

    extra_transpose = 0
    while notation[0] in ('#', 'b'):
        if notation[0] == '#':
            extra_transpose += 1
        elif notation[0] == 'b' :
            extra_transpose -= 1
        notation = notation[1:]

    for i in notation.lower():
        if not (i == 'i' or i == 'v') or already_found_numeral:
            rest += i
            already_found_numeral = True
        else:
            roman_numeral += i

    chord_number = roman_numerals[roman_numeral]

    transpose = extra_transpose + semitone_offsets[chord_number]

    is_minor = roman_numeral[0] == notation[0]

    if rest == "":
        # we know its just major
        return Triad(minor=is_minor, transpose=transpose)
    else:
        raise Exception("Don't know how to handle a chord notation: %s" % (rest))




def progression(base, progression):
    """

    progression should be like:

    "I-IV-V-IV"

    "I-iii-IV"

    """

    return [from_notation(c) for c in progression.split("-")]

    

