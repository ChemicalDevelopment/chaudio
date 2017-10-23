"""

displays a waveform

"""

import chaudio

import waveforms as wf
import plugins
import freq

import argparse


parser = argparse.ArgumentParser(description='show analysis on waveform')

parser.add_argument("-w", default="data = wf.sin(t, hz)", help='generate waveform')
parser.add_argument("-t", default=1.0, type=float, help='time')
parser.add_argument("-hz", default="1.0", type=str, help='frequency')
parser.add_argument("-mhz", default=100, type=float, help='max frequency to graph')
parser.add_argument("-o", "--output", default=None, type=str, help='output file')
parser.add_argument("-g", action="store_true", help='max frequency to graph')

args = parser.parse_args()

t = chaudio.times(args.t)
hz = eval(args.hz)

# read in our file
data = eval(args.w)

if args.output is not None:
    chaudio.tofile(args.output, data)


if args.g:
    import viewer

    viewer.show_data(data)
    #viewer.show_frequency_graph(data, maxfreq=args.mhz)

    input("press enter to close")




