#!/usr/bin/env python3

#import sys
#from os import listdir, mkdir
from os.path import isfile, join, isdir
from collections import defaultdict 
#import copy
#import spacy
#import scispacy
import sys, getopt


PROG_NAME = "collect-umls-hierarchy.py"

# all columns values are zero-indexed

INPUT_COL_CONCEPT_ID = 0

UMLS_REL_COL_CUI1 = 0
UMLS_REL_COL_STYPE1 = 2
UMLS_REL_COL_REL = 3
UMLS_REL_COL_CUI2 = 4
UMLS_REL_COL_STYPE2 = 6

UMLS_SEP = '|'
UMLS_REL_FILE = "MRREL.RRF"

PARENT_REL = "RN"
INCLUDE_RELATED_CONCEPTS = []
MAX_DEPTH = None

def usage(out):
    print("Usage: cat <concepts> | "+PROG_NAME+" [options] <UMLS dir> <output file> ",file=out)
    print("",file=out)
    print("  Reads a list of CUI concepts (one by line) from STDIN and extracts from the UMLS data all",file=out)
    print("  their 'descendants' according to the UMLS hierarchy.",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
    print("    -r reverse mode: collect all the ancestors of the concepts.",file=out)
    print("    -i include close concepts 'related and possibly synonymous' (RQ)",  file=out)
    print("    -I include close related concepts (synonymous and others) (RQ and RO)",  file=out)
    print("    -d <depth> Maximum depth level of the search.",file=out)
    print("",file=out)


def retrieve_related_concepts(umls_relations,current_level_cuis, collected, depth):
    new_cuis = set()
    for rel in INCLUDE_RELATED_CONCEPTS:
        new_cuis = set()
        for cui1 in current_level_cuis:
            for cui2 in umls_relations[cui1][rel]:
                collected[cui2].append(str(depth)+","+cui1+","+rel)
                new_cuis.add(cui2)
    return new_cuis


# main

try:
    opts, args = getopt.getopt(sys.argv[1:],"hriId:")
except getopt.GetoptError:
    usage(sys.stderr)
    sys.exit(2)
for opt, arg in opts:
    if opt == "-h":
        usage(sys.stdout)
        sys.exit()
    elif opt == "-r":
        PARENT_REL = "RB"
    elif opt == "-i":
        INCLUDE_RELATED_CONCEPTS = [ "RQ" ]
    elif opt == '-I':
        INCLUDE_RELATED_CONCEPTS = [ "RQ", "RO" ]
    elif opt == '-d':
        MAX_DEPTH = int(arg)

#print("debug args after options: ",args)

if len(args) != 2:
    usage(sys.stderr)
    sys.exit(2)

umlsDir = args[0]
output_file = args[1]

current_level_cuis = set([ s.rstrip() for s in sys.stdin ])
collected = defaultdict(list)
for cui in current_level_cuis:
    collected[cui].append("0,NA,NA")

# relations[cui1][rel-type] = list of cui2
umls_relations = defaultdict(lambda: defaultdict(list))
f= join(umlsDir, "META", UMLS_REL_FILE)
with open(f) as infile:
    for line in infile:
        cols = line.rstrip().split(UMLS_SEP)
        if cols[UMLS_REL_COL_STYPE1] == 'CUI' and cols[UMLS_REL_COL_STYPE2] == 'CUI':
            cui1 = cols[UMLS_REL_COL_CUI1]
            cui2 = cols[UMLS_REL_COL_CUI2]
            rel = cols[UMLS_REL_COL_REL]
            umls_relations[cui1][rel].append(cui2)


related = retrieve_related_concepts(umls_relations,current_level_cuis, collected, 0)
current_level_cuis.union(related)
done = False
depth = 1
while len(current_level_cuis)>0 and (MAX_DEPTH is None or depth <= MAX_DEPTH):
    new_cuis = set()
    for cui1 in current_level_cuis:
        for cui2 in umls_relations[cui1][PARENT_REL]:
            collected[cui2].append(str(depth)+","+cui1+","+PARENT_REL)
            new_cuis.add(cui2)
    related = retrieve_related_concepts(umls_relations, new_cuis, collected, depth)
    new_cuis.union(related)
    current_level_cuis = new_cuis
    depth += 1

with open(output_file,"w") as outfile:
    for cui, cui_details in collected.items():
        outfile.write(cui+"\t"+" ".join(cui_details)+"\n")


