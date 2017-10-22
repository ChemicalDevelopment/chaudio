"""

how to read in a file

"""

import chaudio
import viewer

import argparse


parser = argparse.ArgumentParser(description='Read in an audio file and show analysis')

parser.add_argument("file", default=None, help='file to process')
parser.add_argument("-g", "--graph", default=["freq"], nargs="+", help='to graph (freq, data)')

args = parser.parse_args()

if args.file == None:
    print ("Please enter an audio file name")
    exit(1)

# read in our file
data = chaudio.fromfile(args.file, combine=True)

thingsgraphed = 0

if "freq" in args.graph:
    thingsgraphed += 1
    viewer.show_frequency_graph(data)

if "data" in args.graph:
    thingsgraphed += 1
    viewer.show_data(data)

if thingsgraphed != len(args.graph):
    print ("Warning: you specified more --graph options than were displayed. You probably entered invalid choices")



input("press enter to close")




