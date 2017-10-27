"""

frequency manipulation

"""


valid_note_names = {
    "Ab": 25.95654359874657, 
    "A": 27.5, 
    "A#": 29.13523509488062, 
    "Bb": 29.13523509488062, 
    "B": 30.867706328507758, 
    "C": 32.70319566257483,
    "C#": 34.64782887210901, 
    "Db": 34.64782887210901, 
    "D": 36.70809598967595, 
    "D#": 38.890872965260115, 
    "Eb": 38.890872965260115, 
    "E": 41.20344461410874, 
    "F": 43.653528929125486, 
    "F#": 46.2493028389543, 
    "Gb": 46.2493028389543, 
    "G": 48.99942949771866,
    "G#": 51.91308719749314, 
}

valid_octaves = [0, 1, 2, 3, 4, 5, 6, 7, 8]


# cents are a measurement of pitch change, +1200 cents = 1 octave, +100 = half step (like C to C#)
def transpose(hz, cents=0):
    return hz * 2.0 ** (cents / 1200.0)


def note(name):
    note_name = ""
    for i in name:
        if not i.isdigit():
            note_name += i
        else:
            break
    octave_number = name.replace(note_name, "")

    if octave_number == "":
        octave_number = 4
    else:
        octave_number = int(octave_number)

    if note_name not in valid_note_names.keys():
        raise ValueError("invalid note name: %s" % (note_name))

    if octave_number not in valid_octaves:
        raise ValueError("invalid octave number: %s" % (octave_number))

    return valid_note_names[note_name] * (2.0 ** octave_number)
    
    