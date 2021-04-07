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
    print("Usage: "+PROG_NAME+" [options] <year> <doc level> <input prefix> <output .dcm file>",file=out)
    print("",file=out)
    print("  Reads  TDC files <input prefix>.raw and <input prefix>.cuis file and writes the",file=out)
    print("   document-concept matrix file, which contains one line by document followed by the list",file=out)
    print("   of concepts in the document:",file=out)
    print("     <year> <doc id> <list of doc-concepts>",file=out)
    print("  Where <list of doc-concepts> contains a space separated list of strings '<concept id>"+OUTPUT_CONCEPT_FREQ_SEP+"<freq>'.",file=out)
    print("    Note1: the separator ':' can appear in <concept id> but not in <freq>.",file=out)
    print("    Note2: in case the concept id contains a space, double quotes are added: \"<id>:<freq>\".",file=out)
    print("    Note3: the .raw file is used to get all the PMIDs (even for empty documents),",file=out)
    print("           but only if level='doc' (it wouldn't make sense to add empty sentences).",file=out)
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
    opts, args = getopt.getopt(sys.argv[1:],"hk")
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

if len(args) != 4:
    usage(sys.stderr)
    sys.exit(2)

year = args[0]
doc_level = args[1]
input_prefix = args[2]
output_file = args[3]


#docs = defaultdict(list)
docs = defaultdict(lambda: defaultdict(int))

# 1) read .raw file to collect the pmids only if level='doc'
if doc_level == "doc":
    input_file = input_prefix+".raw"
    with open(input_file) as infile:
        for line in infile:
            cols = line.split("\t")
            key = cols[COL_PMID]
            docs[key] = defaultdict(int)

# 2) read .cuis file
input_file = input_prefix+".cuis"
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
    concepts_list = list()
    for concept,freq in doc_map.items():
        s = concept+OUTPUT_CONCEPT_FREQ_SEP+str(freq)
        if concept.find(" ") >= 0:
            s = '"'+s+'"'
        concepts_list.append(s)
    outfile.write("%s\t%s\t%s\n" % (year, doc_key, " ".join(concepts_list)) )

    
outfile.close()

sys.exit()



