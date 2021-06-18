#!/usr/bin/env python3

#import sys
from os import listdir, makedirs
from os.path import isfile, join, isdir
from collections import defaultdict 
#import copy
#import spacy
#import scispacy


import sys, getopt


PROG_NAME = "classify-cooccurrences-by-target.py"



PTC_INPUT = False
TARGETS_FILENAME = 'targets.tsv'  
INPUT_CONCEPT_FREQ_SEP=":"
SEPARATOR_CONCEPT_ID_TYPE = "@"


def usage(out):
    print("Usage: cat <targets file> | "+PROG_NAME+" [options] <indiv freq file> <joint freq file> <output dir>",file=out)
    print("",file=out)
    print("  Generates a file containing the list of related concepts for every target concept as well",file=out)
    print("  as a file containing the list of target concepts, both of which with including frequency,",file=out)
    print("  term string and groups.",file=out)
    print("",file=out)
    print("  Input: ",file=out)
    print("    - <indiv freq file> is formatted as: <concept> <unique freq> <multi freq> <term> <groups>",file=out)
    print("    - <joint freq file> is formatted as: <concept1> <concept2> <joint frequency>",file=out)
    print("    Additionally a list of target concepts is read from STDIN, one by line.",file=out)
    print("  Output:",file=out)
    print("    - <output dir>/targets.tsv formatted as: <target> <unique freq> <term> <groups>",file=out)
    print("    - <output dir>/<target> formatted as: <concept> <indiv freq> <term> <groups> <joint freq>",file=out)
    print("",file=out)
    print("  Options")
    print("    -h: print this help message.",file=out)
    print("    -t <targets filename>: filename for the targets output; default: '"+TARGETS_FILENAME+"'",file=out)
    print("    -p PTC input: remove MESH prefix from <joint freq file> concept ids.",file=out)
    print("",file=out)


def remove_mesh_prefix(s):
    if s[0:5] == "MESH:":
        return s[5:]
    else:
        return s

def write_cooc_to_target_file(out_file, this_concept, this_concept_info, joint_freq):
    if out_file is None:
        raise Exception("BUG. The file handle should exist.")
    out_file.write("%s\t%s\t%s\t%s\t%s\n" % (this_concept, this_concept_info[0], this_concept_info[1], this_concept_info[2], freq))


# main

try:
    opts, args = getopt.getopt(sys.argv[1:],"ht:p")
except getopt.GetoptError:
    usage(sys.stderr)
    sys.exit(2)
for opt, arg in opts:
    if opt == "-h":
        usage(sys.stdout)
        sys.exit()
    elif opt == "-t":
        TARGETS_FILENAME = arg
    elif opt == "-p":
        PTC_INPUT = True
#print("debug args after options: ",args)

if len(args) != 3:
    usage(sys.stderr)
    sys.exit(2)

indiv_file = args[0]
joint_file = args[1]
output_dir = args[2]

target_concepts = [ line.rstrip() for line in sys.stdin ]

makedirs(output_dir, exist_ok=True)

concept_info = dict()
with open(indiv_file) as infile:
    for line in infile:
        cols = line.rstrip('\n').split('\t')
        c = cols[0]
        if concept_info.get(c) is None:
            concept_info[c] = (cols[1], cols[3], cols[4])
        else:
            raise Exception("Error: concept '"+c+"' found at least twice in '"+indiv_file+"'")


f = join(output_dir, TARGETS_FILENAME)
targets_files = dict()
with open(f,"w") as out_file:
    for target in target_concepts:
        data = concept_info.get(target)
        if data is None:
            raise Exception("Error: cannot find target '"+target+"' in '"+indiv_file+"'")
        out_file.write("%s\t%s\t%s\t%s\n" % (target, data[0], data[1], data[2]))
        ft = join(output_dir, target)
        targets_files[target] = open(ft,"w")

nb_total = 0
nb_no_target = 0
with open(joint_file) as infile:
    for line in infile:
        nb_total += 1
        cols = line.rstrip('\n').split('\t')
        c1 = cols[0]
        c2 = cols[1]
        if PTC_INPUT:
            c1 = remove_mesh_prefix(c1)
            c2 = remove_mesh_prefix(c2)
        freq = cols[2]
        c1_info = concept_info.get(c1)
        c2_info = concept_info.get(c2)
        at_least_one_target = False
        if c1 in target_concepts:
            at_least_one_target = True
            if c2_info is None:
                raise Exception("Error: cannot find concept '"+c2+"' in '"+indiv_file+"'")
            write_cooc_to_target_file(targets_files[c1], c2, c2_info,freq)
        if c2 in target_concepts:
            at_least_one_target = True
            if c1_info is None:
                raise Exception("Error: cannot find concept '"+c1+"' in '"+indiv_file+"'")
            write_cooc_to_target_file(targets_files[c2], c1, c1_info,freq)
        if not at_least_one_target:
            nb_no_target += 1
if nb_no_target > 0:
    print("Warning: no target found for %d joint pairs of concepts out of %d." % (nb_no_target, nb_total) ,file=sys.stderr)


for target, f in targets_files.items():
    f.close()
