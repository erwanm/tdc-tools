#import sys
#from os import listdir, mkdir
#from os.path import isfile, join, isdir
from collections import defaultdict 
#import copy
#import spacy
#import scispacy


import sys, getopt


PROG_NAME = "build-doc-concept-matrix.py"

# .cuis format:
COL_PMID = 0
COL_PARTID = 1
COL_ELEMID = 2
COL_SENTID = 3
COL_CONCEPT = 4
COL_POS = 5
COL_LENGTH = 6
  
INPUT_MULTI_CONCEPT_SEP=","
OUTPUT_CONCEPT_FREQ_SEP=":"

def usage(out):
    print("Usage: "+PROG_NAME+" [options] <year> <doc level> <input .cuis file> <output .dcm file>",file=out)
    print("",file=out)
    print("  Reads a TDC .cuis file and writes the document-concept matrix file, which contains one",file=out)
    print("  line by document followed by the list of concepts in the document:",file=out)
    print("    <year> <doc id> <list of doc-concepts>",file=out)
    print("  Where <list of doc-concepts> contains a space separated list of strings '<concept id>"+OUTPUT_CONCEPT_FREQ_SEP+"<freq>'.",file=out)
    print("    Note: the separator ':' can appear in <concept id> but not in <freq>.",file=out)
    print("  <doc level> indicates which portion of a Medline/PMC entry is considered as a document:",file=out)
    print("    'doc', 'part', 'elem' or 'sent'",file=out)
    print("",file=out)
    print("  Options")
    print("    -h: print this help message.",file=out)
    print("    -k: KD format: the concept value is a comma-separated list of concepts.",file=out)
    print("",file=out)


def get_doc_key(doc_level, columns):
    key = columns[COL_PMID]
    if doc_level != "doc":
        key += ","+columns[COL_PARTID]
        if doc_level != "part":
            key += ","+columns[COL_ELEMID]
            if doc_level != "elem":
                key += ","+columns[COL_SENTID]
                if doc_level != "sent":
                    print("Error: invalid doc level id '"+doc_level+"'. Must be 'doc', 'part', 'elem' or 'sent'.", file=sys.stderr)
                    sys.exit(3)
    return key



# main

input_multi_concept = False
try:
    opts, args = getopt.getopt(sys.argv,"hk")
except getopt.GetoptError:
    usage(sys.stderr)
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        usage(sys.stdout)
        sys.exit()
    elif opt == '-k':
        input_multi_concept = True
#      elif opt in ("-o", "--ofile"):
#         outputfile = arg

# print("debug args after options: ",args)

if len(args) != 5:
    usage(sys.stderr)
    sys.exit(2)

year = args[1]
doc_level = args[2]
input_file = args[3]
output_file = args[4]


#docs = defaultdict(list)
docs = defaultdict(lambda: defaultdict(int))

with open(input_file) as infile:
    for line in infile:
        cols = line.split("\t")
        if input_multi_concept:
            concepts = cols[COL_CONCEPT].split(INPUT_MULTI_CONCEPT_SEP)
        else:
            concepts = [ cols[COL_CONCEPT] ] 
        key = get_doc_key(doc_level, cols)
        for c in concepts:
            docs[key][c] += 1

outfile = open(output_file,"w")
for doc_key,doc_map in docs.items():
    concepts_list = [ concept+OUTPUT_CONCEPT_FREQ_SEP+str(freq) for concept,freq in doc_map.items() ]
    outfile.write("%s\t%s\t%s\n" % (year, doc_key, " ".join(concepts_list)) )

    
outfile.close()

sys.exit()



