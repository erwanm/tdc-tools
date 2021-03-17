#import sys
#from os import listdir, mkdir
from os.path import isfile, join, isdir
from collections import defaultdict 
#import copy
#import spacy
#import scispacy


import sys, getopt


PROG_NAME = "get-frequency-from-doc-concept-matrix.py"

  
INPUT_CONCEPT_FREQ_SEP=":"

def usage(out):
    print("Usage: ls <input files> | "+PROG_NAME+" [options] <output file> [target concepts file]",file=out)
    print("",file=out)
    print("  Reads a list of input .dcm files (doc concept matrix format) provided on STDIN, then",file=out)
    print("  calculates either the individual or the joint frequency for all/some of the concepts.",file=out)
    print("  The input files must all belong to the same year, but may come from different variants",file=out)
    print("  of the data (e.g. abstracts, articles).",file=out)
    print("  It is recommended to provide the optional argument [target concepts file] for joint",file=out)
    print("  frequency, not for individual frequency.",file=out)
    print("",file=out)
    print("  The default is to calculate the individual frequency for every concept and write two files:",file=out)
    print("    * <output file> contains the counts as:",file=out)
    print("        <year> <concept id> <doc frequency> <occurences frequency>",file=out)
    print("    * <output file>.total contains a single line:",file=out)
    print("        <year> <nb unique concepts> <nb docs> <nb concepts occurrences>",file=out)
    print("    Notes:", file=out)
    print("      - the regular 'doc as set' probability is <doc frequency> / <nb docs>",file=out)
    print("      - the 'doc as multiset' probability is <occurences frequency> / <nb concepts occurrences>",file=out)
    print("",file=out)
    print("  Use option -j <target concepts file> to calculate the joint frequency for the list of target",file=out)
    print("  concepts in <target concepts file> (one by line). In this case <output file> contains:",file=out)
    print("    <year> <concept1> <concept2> <joint freq>",file=out)
    print("    Note 1: the joint probability is <joint freq> / <nb docs> (obtained from the indiv .total file)",file=out)
    print("    Note 2: evry pair of concept A,B is written only once using lexicographic order (concept1<concept2).",file=out)
    print("",file=out)
    print("  Options")
    print("    -h: print this help message.",file=out)
    print("    -j: joint frequency for all pairs of concepts where at least one concept belongs to the",file=out)
    print("        list of targets.",file=out)
    print("    -J: joint frequency only for pairs of concepts where both concepts belong to the list of targets.",file=out)
    print("",file=out)





# main

joint_mode = False
joint_both_target = False
try:
    opts, args = getopt.getopt(sys.argv[1:],"hjJ")
except getopt.GetoptError:
    usage(sys.stderr)
    sys.exit(2)
for opt, arg in opts:
    if opt == "-h":
        usage(sys.stdout)
        sys.exit()
    elif opt == "-j":
        joint_mode = True
    elif opt == "-J":
        joint_mode = True
        joint_both_target = True
#         outputfile = arg

#print("debug args after options: ",args)

if len(args) != 1 and len(args) != 2:
    usage(sys.stderr)
    sys.exit(2)

output_file = args[0]
targetsFile = None
if len(args) == 2:
    targetsFile = args[1]


if joint_mode and targetsFile is None:
    print("Warning: no list of targets with joint mode.", file=sys.stderr)
    # ignoring joint_both_target option anyway:
    joint_both_target = False


# Step 1: read input files and check them
input_files = [ f.rstrip() for f in sys.stdin ]
for filename in input_files:
    if not isfile(filename):
        raise Exception("File '"+filename+"' read from STDIN does not exist.")


# Step 2: read target concepts if provided
target_concepts = None
if targetsFile is not None:
    with open(targetsFile) as infile:
        target_concepts = set([ l.rstrip() for l in infile ])


# Step 3: counting
year = None
nb_docs = 0
indiv_set = defaultdict(int)
indiv_multi = defaultdict(int)
joint = defaultdict(lambda: defaultdict(int))
for input_file in input_files:
    with open(input_file) as f:
        for l in f:
            line = l.rstrip()
#            print("DEBUG line = '"+line+"'",file=sys.stderr)
            cols = line.split('\t')
            nb_docs += 1
            doc_set = set()
            if len(cols) != 3:
                raise Exception("Invalid format in file '"+input_file+"': '"+line+"'") 
            year_doc = cols[0]
            if year is None:
                year = year_doc
            else:
                if year_doc != year:
                    raise Exception("Inconsistent year in '"+input_file+"': '"+line+"' (previously the year was "+str(year)+")") 
            doc_id = cols[1]
            concepts_list = cols[2]
            for concept_freq_str in concepts_list.split(" "):
                s = concept_freq_str.rfind(INPUT_CONCEPT_FREQ_SEP)
                concept = concept_freq_str[:s]
                freq = concept_freq_str[s+1:]
 #               print("DEBUG concept = '%s', freq = '%s'" % (concept, freq),file=sys.stderr )
                doc_set.add(concept)
                if not joint_mode:
                    indiv_multi[concept] += int(freq)
            if joint_mode:
                for c1 in doc_set:
                    c1_target = target_concepts is None or c1 in target_concepts
                    if not joint_both_target or c1_target:
                        for c2 in doc_set:
                            if c1 < c2:
                                c2_target = target_concepts is None or c2 in target_concepts
                                if (targetsFile is None) or (joint_both_target and c1_target and c2_target) or (not joint_both_target and (c1_target or c2_target)):
                                    joint[c1][c2] += 1
            else:
                for c in doc_set:
                    indiv_set[c] += 1 

with open(output_file, "w") as outfile:
    if joint_mode:
        for c1,c1_map in joint.items():
            for c2, joint_freq in c1_map.items():
                outfile.write("%s\t%s\t%s\t%d\n" % (year, c1, c2, joint_freq ) )
    else:
        total_multi_concepts = 0
        for concept, indiv_freq in indiv_set.items():
            multi_freq = indiv_multi[concept]
            total_multi_concepts += multi_freq
            outfile.write("%s\t%s\t%d\t%d\n" % (year, concept, indiv_freq, multi_freq ) )
        with open(output_file+".total", "w") as outfile_total:
            outfile_total.write("%s\t%d\t%d\t%d\n" % (year, len(indiv_set.keys()), nb_docs, total_multi_concepts) )
        
