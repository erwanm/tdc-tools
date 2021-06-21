#!/usr/bin/env python3

#import sys
#from os import listdir, mkdir
from os.path import isfile, join, isdir
from collections import defaultdict 
#import copy
#import spacy
#import scispacy
import sys, getopt


PROG_NAME = "convert-umls-to-mesh.py"

# all columns values are zero-indexed

INPUT_COL_CONCEPT_ID = 0
UMLS_COL_CUI = 0
UMLS_COL_LANG = 1
UMLS_LANG_FILTER_VAL = [ "ENG" ]
UMLS_COL_PREFERED = 6
UMLS_COL_SOURCE = 11
UMLS_MESH_SOURCE_FILTER_VAL = "MSH"
UMLS_COL_MESH_ID = 10
UMLS_COL_TERM = 14

UMLS_SEP = '|'
UMLS_MAIN_FILE = "MRCONSO.RRF"

OUTPUT_SEP = " " 

REVERSE_MODE = False
FILTER_PREFERED = True


def usage(out):
    print("Usage: ls <input files> | "+PROG_NAME+" [options] <UMLS dir> <output suffix> ",file=out)
    print("",file=out)
    print("  Reads a list of input tsv files with a concept id column (a UMLS CUI by default) and",file=out)
    print("  maps the id to the corresponding Mesh descriptor (default) using the UMLS data.  ",file=out)
    print("  For each input file <f> an output file <f><output suffix> is created with an additional",file=out)
    print("  column. ",file=out)
    print("  <UMLS dir> is the UMLS metathesaurus data, it must contain RRF files: <UMLS dir>/META/*.RRF",file=out)
    print("",file=out)
    print("  Caution: in general an input concept id may have any number of output ids (possibly zero).",file=out)
    print("           As a result the new column contains (in general) a list of ids which could be empty.",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
    print("    -i <id col>: concept id col; default: "+str(INPUT_COL_CONCEPT_ID)+".",file=out)
    print("    -r: reverse mode, i.e. conversion from Mesh to UMLS.",file=out)
    print("    -p: do not restrict to prefered terms (default: yes).",file=out)
#    print("    -m Mesh ids instead of default UMLS CUI ids (CUI is the default).",  file=out)
#    print("    -p PTC input: the concept is represented as <id>@<category>, and a Mesh id has a ",file=out)
#    print("       prefix 'MESH:'. Both the category and the prefix are removed. Implies '-m'.",file=out)
#    print("    -g <UMLS sem groups file> add 'semantic group' column using UMLS group hierarchy which",file=out)
#    print("       can be downloaded at https://lhncbc.nlm.nih.gov/semanticnetwork/download/SemGroups.txt",file=out)
#    print("    -G add 'semantic group' column using PTC annotated type (requires PTC input; implies -p and -m)",file=out)
#    print("    -l filter only English language terms. This can be produce 'NA' terms if a concept does ",file=out)
#    print("       not have any English term (this is rare but it happens). By default English is prefered")
#    print("       but non-English is used if no English term is found.",file=out)
    print("",file=out)



# main

umlsGroupFile = None
try:
    opts, args = getopt.getopt(sys.argv[1:],"hr")
except getopt.GetoptError:
    usage(sys.stderr)
    sys.exit(2)
for opt, arg in opts:
    if opt == "-h":
        usage(sys.stdout)
        sys.exit()
    elif opt == "-i":
        INPUT_COL_CONCEPT_ID = int(arg) -1
    elif opt == "-r":
        REVERSE_MODE = True
    elif opt == "-p":
        FILTER_PREFERED = False

#print("debug args after options: ",args)

if len(args) != 2:
    usage(sys.stderr)
    sys.exit(2)

umlsDir = args[0]
outputSuffix = args[1]

input_files = [ f.rstrip() for f in sys.stdin ]
for filename in input_files:
    if not isfile(filename):
        raise Exception("File '"+filename+"' read from STDIN does not exist.")


print("INFO: Reading UMLS concepts and terms...")
mapping = defaultdict(set)


f= join(umlsDir, "META", UMLS_MAIN_FILE)
with open(f) as infile:
    for line in infile:
        cols = line.rstrip().split(UMLS_SEP)
        index_lang = 0
        if cols[UMLS_COL_LANG] in UMLS_LANG_FILTER_VAL and cols[UMLS_COL_SOURCE] == UMLS_MESH_SOURCE_FILTER_VAL:    # filter language and Mesh source
            if not FILTER_PREFERED or cols[UMLS_COL_PREFERED] == 'Y':                             # store only if prefered term
                cui = cols[UMLS_COL_CUI]
                mesh = cols[UMLS_COL_MESH_ID]
                if REVERSE_MODE:
                    mapping[mesh].add(cui)
                else:
                    mapping[cui].add(mesh)



print("INFO: Processing input files...")
for input_file in input_files:
    with open(input_file+outputSuffix,"w") as outfile:
        with open(input_file) as infile:
            for line in infile:
                cols = line.rstrip().split('\t')
                concept_id = cols[INPUT_COL_CONCEPT_ID]
                mapped = mapping.get(concept_id)
                if mapped is None:
                    new_col = ""
                else:
                    new_col = OUTPUT_SEP.join(mapped)
                cols.append(new_col)
                outfile.write("\t".join(cols)+"\n")


