#!/usr/bin/env python3

#import sys
#from os import listdir, mkdir
from os.path import isfile, join, isdir
from collections import defaultdict 
#import copy
#import spacy
#import scispacy
import sys, getopt


PROG_NAME = "list-column-to-tidy-format.py"

INPUT_COL = -1 # last column by default
INPUT_SEP=" "
OUTPUT_EMPTY_VALUE="NA"

def usage(out):
    print("Usage: "+PROG_NAME+" [options] <input tsv file> <output tsv file>",file=out)
    print("",file=out)
    print("  Reads <input file> where the last column contains a list of values,",file=out)
    print("  then for every input line the line is duplicated with a single value ",file=out)
    print("  from the list as the last column (similar to the tidy format).",file=out)
    print("  If a line has no value in the last column, it is duplicated only ",file=out)
    print("  once with 'NA' as the last column.",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
    print("    -c <col>: column number of the target multi-valued column; default: last.",file=out)
    print("    -s <separator> the input list of values are separated by this separator; default: '"+INPUT_SEP+"'.",file=out)
    print("    -e <empty value> Use this value when the column is empty; default: '"+OUTPUT_EMPTY_VALUE+"'.",  file=out)
    print("",file=out)



# main

try:
    opts, args = getopt.getopt(sys.argv[1:],"hc:s:e:")
except getopt.GetoptError:
    usage(sys.stderr)
    sys.exit(2)
for opt, arg in opts:
    if opt == "-h":
        usage(sys.stdout)
        sys.exit()
    elif opt == "-c":
        INPUT_COL = int(arg) -1
    elif opt == "-s":
        INPUT_SEP = arg
    elif opt == '-e':
        OUTPUT_EMPTY_VALUE = arg

#print("debug args after options: ",args)

if len(args) != 2:
    usage(sys.stderr)
    sys.exit(2)

input_file = args[0]
output_file = args[1]

with open(input_file) as infile:
    with open(output_file,"w") as outfile:
            for line in infile:
                cols = line.rstrip('\n').split('\t')
                values = cols[INPUT_COL].split(INPUT_SEP)
                # if len(values)==0: # wrong
                if len(values)==0 or (len(values)==1 and values[0] == ""):
                    values = [OUTPUT_EMPTY_VALUE]
                for val in values:
                    out_cols = cols.copy()
                    out_cols[INPUT_COL] = val
                    outfile.write("\t".join(out_cols)+"\n")

