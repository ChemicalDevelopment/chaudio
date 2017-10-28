"""

reading in a file, add noise and then output it

"""

# accept commandline arguments
import argparse

import chaudio

parser = argparse.ArgumentParser(description='Add noise to audio')

parser.add_argument("file", default=None, help='file to process')
parser.add_argument("-o", "--output", default="addnoise.wav", help='output file')
parser.add_argument("-n", "--noise", default=.08, type=float, help='how much noise to add')

args = parser.parse_args()

if args.file == None:
    print ("Please supply an audio file name")
    exit(1)

# read in our file
r = chaudio.fromfile(args.file)

# add static
r = r + args.noise * chaudio.waves.noise(chaudio.times(r))

# output to file
chaudio.tofile(args.output, r)

