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
ldata, rdata = chaudio.fromfile(args.file, _channels=2)

# add static to both sides
ldata += .05 * chaudio.waveforms.noise(chaudio.times(ldata))
rdata += .05 * chaudio.waveforms.noise(chaudio.times(rdata))

# output to file
chaudio.tofile(args.output, (ldata, rdata))

