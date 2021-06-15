#import sys
#from os import listdir, mkdir
from os.path import isfile, join, isdir
from collections import defaultdict 
#import copy
#import spacy
#import scispacy
import sys, getopt


PROG_NAME = "ptc-aggregate-across-types.py"

CONCEPTS_COLS="1"
KEEP_GROUPS=False


SEPARATOR_CONCEPT_ID_TYPE = "@"
OUTPUT_GROUP_SEP=" "


def usage(out):
    print("Usage: "+PROG_NAME+" [options] <input file> <output file> ",file=out)
    print("",file=out)
    print("  Reads an input file containing PTC concepts in the form <id>@<type> and sums the ",file=out)
    print("  frequencies correponding to the same <id>.",file=out)
    print("  All the columns are assumed to contain frequencies except the concept column(s).",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
    print("    -t: keep list of types after aggregating; possible only with a single concept column.",file=out)
    print("    -c: <concepts column(s)> default = "+CONCEPT_COLS,file=out)
    print("    -j: joint freq file -> concept cols = 1,2; freq cols = 3 ",file=out)
    print("",file=out)



# main

try:
    opts, args = getopt.getopt(sys.argv[1:],"htc:j")
except getopt.GetoptError:
    usage(sys.stderr)
    sys.exit(2)
for opt, arg in opts:
    if opt == "-h":
        usage(sys.stdout)
        sys.exit()
    elif opt == "-t":
        KEEP_GROUPS=True
    elif opt == "-c":
        CONCEPTS_COLS=arg
    elif opt == '-j':
        CONCEPTS_COLS="1,2"

#print("debug args after options: ",args)

if len(args) != 2:
    usage(sys.stderr)
    sys.exit(2)

input_file = args[0]
output_file = args[1]

concepts_cols = [ int(c)-1 for c in CONCEPTS_COLS.split(",") ]
if KEEP_GROUPS and len(concepts_cols)>1:
    raise Exception("Error: cannot have -t with more than one concept column.")

freq = None
groups = defaultdict(set)
with open(input_file) as infile:
    for line in infile:
        cols = line.rstrip().split('\t')
        if freq is None:
            freq = defaultdict(lambda: [0] * (len(cols)-len(concepts_cols)))
        concept_values = [ cols[i] for i in concepts_cols ]
        freq_values = [ int(cols[i]) for i in range(len(cols)) if i not in concepts_cols ]

        concepts = list()
        ptc_category = None
        for concept in concept_values:
            sep_pos = concept.rfind(SEPARATOR_CONCEPT_ID_TYPE)
            if sep_pos != -1:
                ptc_category = concept[sep_pos+1:]
                concept_id = concept[0:sep_pos]
            else:
                print("Warning: no type found in concept '"+concept+"'",file=sys.stderr)
                ptc_category = "NA"
                concept_id = concept
            concepts.append(concept_id)
        concepts_key = "\t".join(concepts)

        for freq_index, freq_val in enumerate(freq_values):
            freq[concepts_key][freq_index] += freq_val

        if KEEP_GROUPS:
            groups[concepts_key].add(ptc_category)


with open(output_file,"w") as outfile:
    for concept_key, list_freq in freq.items():
        concept_cols = concept_key
        if KEEP_GROUPS:
            concept_cols += SEPARATOR_CONCEPT_ID_TYPE+OUTPUT_GROUP_SEP.join(list(groups[concept_key]))
        outfile.write(concept_cols+"\t"+"\t".join([str(freq) for freq in list_freq])+"\n")
