"""

reading in a file, add noise and then output it

"""

import chaudio

# accept commandline arguments
import argparse

parser = argparse.ArgumentParser(description='Add noise to a file')

parser.add_argument("file", default=None, help='file to process')
parser.add_argument("-o", "--output", default="addnoise.wav", help='output file')

args = parser.parse_args()

if args.file == None:
    print ("Please supply an audio file name")
    exit(1)

# read in our file
r = chaudio.fromfile(args.file)

# generate static
noise = .05 * chaudio.waveforms.noise(chaudio.times(r))

# add static
r = r + noise

# output to file
chaudio.tofile(args.output, r)

