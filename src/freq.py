"""

Common frequencies, all are in hz

https://pages.mtu.edu/~suits/notefreqs.html

Also tools to convert and get others in the scale (equal temperment)

As well as functions to return tuples of chords

"""


# reference frequencies

C4 = 261.63
D4 = 293.66
E4 = 329.63
F4 = 349.23
G4 = 392.00
A4 = 440.00
B4 = 493.88


# returns `up` octaves above `note`
def octave(note, up=1):
    return note * (2.0 ** up)

# returns the second of the note (major or minor)
def second(note, minor=False):
    if minor:
        return 1.05946 * note
    else:
        return 1.12246 * note

# returns the third of the note
def third(note, minor=False):
    if minor:
        return 1.18921 * note
    else:
        return 1.25992 * note

# returns fourth
def fourth(note):
    return 1.33483 * note

# returns fifth (major/minor or diminished)
def fifth(note, diminished=False):
    if diminished:
        return 1.41421 * note
    else:
        return 1.49831 * note

# returns sixth (major or minor)
def sixth(note, minor=False):
    if minor:
        return 1.58740 * note
    else:
        return 1.68179 * note

# returns seventh (major or minor)
def seventh(note, minor=False):
    if minor:
        return 1.78180 * note
    else:
        return 1.88775 * note


### CHORDS

# major/minor chord for a key
def chord(note, minor=False):
    return [note, third(note, minor), fifth(note)]


### GENERATED FROM INITIAL FREQUENCIES

C0 = octave(C4, -4)
C1 = octave(C4, -3)
C2 = octave(C4, -2)
C3 = octave(C4, -1)
# already defined
C5 = octave(C4, 1)
C6 = octave(C4, 2)
C7 = octave(C4, 3)
C8 = octave(C4, 4)

D0 = octave(D4, -4)
D1 = octave(D4, -3)
D2 = octave(D4, -2)
D3 = octave(D4, -1)
# already defined
D5 = octave(D4, 1)
D6 = octave(D4, 2)
D7 = octave(D4, 3)
D8 = octave(D4, 4)

E0 = octave(E4, -4)
E1 = octave(E4, -3)
E2 = octave(E4, -2)
E3 = octave(E4, -1)
# already defined
E5 = octave(E4, 1)
E6 = octave(E4, 2)
E7 = octave(E4, 3)
E8 = octave(E4, 4)

F0 = octave(F4, -4)
F1 = octave(F4, -3)
F2 = octave(F4, -2)
F3 = octave(F4, -1)
# already defined
F5 = octave(F4, 1)
F6 = octave(F4, 2)
F7 = octave(F4, 3)
F8 = octave(F4, 4)

G0 = octave(G4, -4)
G1 = octave(G4, -3)
G2 = octave(G4, -2)
G3 = octave(G4, -1)
# already defined
G5 = octave(G4, 1)
G6 = octave(G4, 2)
G7 = octave(G4, 3)
G8 = octave(G4, 4)

A0 = octave(A4, -4)
A1 = octave(A4, -3)
A2 = octave(A4, -2)
A3 = octave(A4, -1)
# already defined
A5 = octave(A4, 1)
A6 = octave(A4, 2)
A7 = octave(A4, 3)
A8 = octave(A4, 4)

B0 = octave(B4, -4)
B1 = octave(B4, -3)
B2 = octave(B4, -2)
B3 = octave(B4, -1)
# already defined
B5 = octave(B4, 1)
B6 = octave(B4, 2)
B7 = octave(B4, 3)
B8 = octave(B4, 4)


