#!/usr/bin/env python3

#import sys
from os import listdir, mkdir
from os.path import isfile, join, isdir
from collections import defaultdict 
#import copy
#import spacy
#import scispacy


import sys, getopt


PROG_NAME = "build-dcm-from-mesh-descriptors-by-pmid.py"

COL_PMID = 0
COL_YEAR = 1
COL_JOURNAL = 2
COL_TITLE = 3
COL_MESH = 4
  
INPUT_MULTI_CONCEPT_SEP=","
INPUT_MAJOR_YN_SEP="|"
OUTPUT_CONCEPT_FREQ_SEP=":"

major_only= False

def usage(out):
    print("Usage: "+PROG_NAME+" [options] <input file> <output dir>",file=out)
    print("",file=out)
    print("  Reads the file 'mesh-descriptors-by-pmid.deduplicated.tsv' obtained using the KD fork",file=out)
    print("  (see https://github.com/erwanm/knowledgediscovery#extracting-mesh-descriptors-by-pmid-from-medline),", file =out)
    print("  then generates all the document-concept matrix files by year: one line by document followed by the list",file=out)
    print("   of concepts in the document:",file=out)
    print("     <year> <doc id> <list of doc-concepts>",file=out)
    print("  Where <list of doc-concepts> contains a space separated list of strings '<concept id>"+OUTPUT_CONCEPT_FREQ_SEP+"<freq>'.",file=out)
    print("",file=out)
    print("  Options")
    print("    -h: print this help message.",file=out)
    print("    -m: use only descriptors marked as major in Medline..",file=out)
    print("",file=out)


# main

try:
    opts, args = getopt.getopt(sys.argv[1:],"hm")
except getopt.GetoptError:
    usage(sys.stderr)
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        usage(sys.stdout)
        sys.exit()
    elif opt == '-m':
        major_only = True
#      elif opt in ("-o", "--ofile"):
#         outputfile = arg

# print("debug args after options: ",args)

if len(args) != 2:
    usage(sys.stderr)
    sys.exit(2)

input_file = args[0]
output_dir = args[1]


if not isdir(output_dir):
    mkdir(output_dir)

year_file = {}
with open(input_file) as infile:
    for line in infile:
        cols = line.rstrip("\n").split("\t")
        pmid = cols[COL_PMID]
        year = cols[COL_YEAR]
        mesh = []
        if (len(cols[COL_MESH])>0):
            raw_mesh = cols[COL_MESH].split(INPUT_MULTI_CONCEPT_SEP)
            for s in raw_mesh:
                parts = s.split(INPUT_MAJOR_YN_SEP)
                descr = parts[0]
                major_yn = parts[1]
                if major_yn=='Y' or not major_only:
                    mesh.append(descr+":1")
        f = year_file.get(year)
        if f is None:
            f = open(join(output_dir,year),"w")
            year_file[year] = f
        f.write("%s\t%s\t%s\n" % (year, pmid, " ".join(mesh)) )

for f in year_file.values():
    f.close()
