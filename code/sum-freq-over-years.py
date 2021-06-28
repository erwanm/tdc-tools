#!/usr/bin/env python3

#import sys
from os import listdir, mkdir
from os.path import isfile, join, isdir
from collections import defaultdict 
#import copy
#import spacy
#import scispacy


import sys, getopt


PROG_NAME = "sum-freq-over-years.py"

COLS_CONCEPT_INDIV = [ 1 ]
COLS_COUNT_INDIV = [ 2, 3 ]
COLS_CONCEPT_JOINT = [ 1, 2 ]
COLS_COUNT_JOINT = [ 3 ]
COLS_CONCEPT_TOTAL = [ ]
COLS_COUNT_TOTAL = [ 2, 3 ]
  
def usage(out):
    print("Usage: "+PROG_NAME+" [options] <input dir> <start year> <end year> <output file>",file=out)
    print("",file=out)
    print("  Reads the year files in <input dir> between <start year> and <end year> (inclusive) and",file=out)
    print("  sums the frequency columns.",file=out)
    print("  The <output>.total is computed as well.",file=out)
    print("  By default it is assumed that the directory contains the individual frequency, use option",file=out)
    print("  '-j' for the joint frequency data.",file=out)
    print("",file=out)
    print("  Options")
    print("    -h: print this help message.",file=out)
    print("    -j: joint frequency  instead of individual frequency",file=out)
    print("",file=out)


def cumulate(count_map, id_cols, count_cols, filename):
    with open(filename) as infile:
        for l in infile:
            line = l.rstrip("\n")
            cols = line.split('\t')
            id_val = "\t".join([ cols[id_col] for id_col in id_cols ])
#            print("DEBUG: id_val='"+id_val+"'",file=sys.stderr)
            for count_col in count_cols:
#                print("DEBUG: count_col=",count_col,", val=",cols[count_col],file=sys.stderr)
                count_map[id_val][count_col] += int(cols[count_col])
#            print("DEBUG C0770206=",count_map["C0770206"],file=sys.stderr)


def write_output(count_map,filename):
    with open(filename, "w") as outfile:
        for ids, lcount in count_map.items():
            if (len(ids)>0):
                cols = [ ids ]
            else:
                cols = []
            cols += [ str(count_val) for count_col,count_val in lcount.items() ]
            outfile.write("\t".join(cols)+"\n")


# main

joint_mode = False
try:
    opts, args = getopt.getopt(sys.argv[1:],'hj')
except getopt.GetoptError:
    usage(sys.stderr)
    sys.exit(2)
for opt, arg in opts:
    if opt == "-h":
        usage(sys.stdout)
        sys.exit()
    elif opt == "-j":
        joint_mode = True

#print("debug args after options: ",args)

if len(args) != 4:
    usage(sys.stderr)
    sys.exit(2)

input_dir = args[0]
start_year = int(args[1])
end_year = int(args[2])
output_file = args[3]

count_map = defaultdict(lambda: defaultdict(int))
count_map_total = defaultdict(lambda: defaultdict(int))
files = listdir(input_dir)
for f in files:
    fname = join(input_dir, f)
    year = int(f[0:4])
    if year >= start_year and year <= end_year:
        if len(f) == 4:
            if joint_mode:
                cumulate(count_map, COLS_CONCEPT_JOINT, COLS_COUNT_JOINT, fname)
            else:
                cumulate(count_map, COLS_CONCEPT_INDIV, COLS_COUNT_INDIV, fname)
        else:
            if f == "%04d" % (year)+".total":
                cumulate(count_map_total, COLS_CONCEPT_TOTAL, COLS_COUNT_TOTAL, fname)
            else:
                raise Exception("Error: wrong format in filename '"+fname+"', expecting <year> or <year>.total")

write_output(count_map, output_file)
if not joint_mode: # total file
    write_output(count_map_total, output_file+".total")


