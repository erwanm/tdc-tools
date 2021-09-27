#!/usr/bin/env python3

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
SEPARATOR_CONCEPT_ID_TYPE = "@"

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
    print("      - the total file always counts all the concepts, not only target ones.",file=out)
    print("",file=out)
    print("  Use option -j <target concepts file> to calculate the joint frequency for the list of target",file=out)
    print("  concepts in <target concepts file> (one by line). In this case <output file> contains:",file=out)
    print("    <year> <concept1> <concept2> <joint freq>",file=out)
    print("    Note 1: the joint probability is <joint freq> / <nb docs> (obtained from the indiv .total file)",file=out)
    print("    Note 2: every pair of concept A,B is written only once using lexicographic order (concept1<concept2).",file=out)
    print("",file=out)
    print("  Options")
    print("    -h: print this help message.",file=out)
    print("    -j: joint frequency for all pairs of concepts where at least one concept belongs to the",file=out)
    print("        list of targets.",file=out)
    print("    -J: joint frequency only for pairs of concepts where both concepts belong to the list of targets.",file=out)
    print("    -p: target concepts provided without type are matched against PTC formatted concepts with any type,",file=out)
    print("        for example target 'MESH:D1234567' matches 'MESH:D1234567@XXX' and 'MESH:D1234567@YYY'.",file=out)
    print("    -g <grouping file>: adds some 'meta-concepts' made of the union of several concepts and count them",file=out)
    print("        as well. The file is made of lines <concept> <group>. If target concepts are used, all the",file=out)
    print("        concepts in the groups should also belong to the targets.",file=out)
    print("",file=out)


def fix_spaces_between_quotes_if_any(l):
    currentElem = None
    res = list()
#    print("DEBUG START", file=sys.stderr)
    for e in l:
#        print("  DEBUG elem='"+e+"'", file=sys.stderr)
        if len(e) > 0:
            if currentElem is None:
                if e[0] == '"':
                    if e[-1] == '"' and len(e)>1: # if len(e)==1 it's a single quote so opening (yes, an id starting with a space happens)
                        res.append(e[1:-1])
                    else:
#                        print("  * opening", file=sys.stderr)
                        currentElem = e[1:]
                else:
                    if e[-1] == '"':
                        raise Exception("Error: closing quote does not match anything in ",l)
                    else:
                        res.append(e)
            else:
                if e[0] == '"':
                    raise Exception("Error: opening quote not closed yet but new opening in ",l)
                else:
                    if e[-1] == '"':
                        res.append(currentElem + e[:-1])
#                        print("  * closing", file=sys.stderr)
                        currentElem = None
                    else:
                        currentElem += e
#        else:
#           print("Warning: empty element in list "+"|".join(l),file=sys.stderr)
    if currentElem is not None:
        raise Exception("Error: opening quote not closed at the end in ", l)
    return res
                

def decompose_ptc_concept(ptc_concept):
    sep_pos = ptc_concept.rfind(SEPARATOR_CONCEPT_ID_TYPE)
    if sep_pos == -1:
        return ptc_concept
    else:
        return ptc_concept[0:sep_pos]

# returns true iff doc_concept belongs to target_concepts, modulo type depending on ptc_match_any_type
def concept_in_set(doc_concept, target_concepts, ptc_match_any_type):
    if ptc_match_any_type:
        doc_concept = decompose_ptc_concept(doc_concept)
    return doc_concept in target_concepts

# returns the set corresponding to the concept if present in the 'groups' dict, empty set otherwise
def concept_in_groups_dict(doc_concept, groups, ptc_match_any_type):
    if ptc_match_any_type:
        doc_concept = decompose_ptc_concept(doc_concept)
    return groups[doc_concept]

# main

joint_mode = False
joint_both_target = False
ptc_match_any_type = False
groupingFile = None
try:
    opts, args = getopt.getopt(sys.argv[1:],"hjJpg:")
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
    elif opt == "-p":
        ptc_match_any_type = True
    elif opt == "-g":
        groupingFile = arg

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


groups = defaultdict(set)
if groupingFile is not None:
    with open(groupingFile) as infile:
        for line in infile:
            cols = line.rstrip("\n").split('\t')
            groups[cols[0]].add(cols[1])
        

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
total_unique_concepts = set()
total_multi_concepts = 0
indiv_set = defaultdict(int)
indiv_multi = defaultdict(int)
joint = defaultdict(lambda: defaultdict(int))
for input_file in input_files:
    with open(input_file) as f:
#        print("DEBUG file = '"+input_file+"'",file=sys.stderr)
        for l in f:
            # note: removing the line break '\n' but not any '\t', as the last column (list of <concept>:<freq> pairs) might be empty
            line = l.rstrip("\n")
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
            concepts_list_str = cols[2]
            concepts_list = fix_spaces_between_quotes_if_any(concepts_list_str.split(" "))
            for concept_freq_str in concepts_list:
                s = concept_freq_str.rfind(INPUT_CONCEPT_FREQ_SEP)
                concept = concept_freq_str[:s]
                freq = concept_freq_str[s+1:]
                # print("DEBUG concept_freq_str='%s', s=%d, concept = '%s', freq = '%s'" % (concept_freq_str, s, concept, freq),file=sys.stderr )
                # even if not a target, the concept is always added to the doc set in case of joint mode
                doc_set.add(concept)
                if not joint_mode:
                    # update multi count
                    try:
                        # total: count every concept, whether target or not
                        total_multi_concepts += int(freq)
                        if target_concepts is None or concept_in_set(concept, target_concepts, ptc_match_any_type):
                            indiv_multi[concept] += int(freq)
                        grps = concept_in_groups_dict(concept, groups, ptc_match_any_type)
                        for grp in grps: 
                            indiv_multi[grp] += int(freq)
                    except ValueError:
                        print("File '"+input_file+"' line = '"+line+"'...", file=sys.stderr )
                        print("DEBUG concept = '%s', freq = '%s'" % (concept, freq),file=sys.stderr )
                        raise Exception("Error: Frequency not an int.")
            if joint_mode:
                for c1 in doc_set:
                    c1_target = target_concepts is None or concept_in_set(c1, target_concepts, ptc_match_any_type)
                    if not joint_both_target or c1_target:
                        for c2 in doc_set:
                            if c1 < c2:
                                c2_target = target_concepts is None or concept_in_set(c2, target_concepts, ptc_match_any_type)
                                if (targetsFile is None) or (joint_both_target and c1_target and c2_target) or (not joint_both_target and (c1_target or c2_target)):
                                    groups_c1 = concept_in_groups_dict(c1, groups, ptc_match_any_type).copy()
                                    groups_c1.add(c1)
                                    groups_c2 = concept_in_groups_dict(c2, groups, ptc_match_any_type).copy()
                                    groups_c2.add(c2)
                                    for grp1 in groups_c1:
                                        # if grp1 belongs to groups_c2 it means that c2 belongs to grp1 -> case not counted
                                        if grp1 not in groups_c2:
                                            for grp2 in groups_c2:
                                                if grp2 not in groups_c1:
                                                    joint[grp1][grp2] += 1
                                        
                    for grp in groups: 
                        indiv_set[grp] += 1
            else:
                for c in doc_set:
                    total_unique_concepts.add(c)
                    if target_concepts is None or concept_in_set(c, target_concepts, ptc_match_any_type):
                        indiv_set[c] += 1 
                    grps = concept_in_groups_dict(c, groups, ptc_match_any_type)
                    for grp in grps: 
                        indiv_set[grp] += 1


with open(output_file, "w") as outfile:
    if joint_mode:
        for c1,c1_map in joint.items():
            for c2, joint_freq in c1_map.items():
                outfile.write("%s\t%s\t%s\t%d\n" % (year, c1, c2, joint_freq ) )
    else:
        for concept, indiv_freq in indiv_set.items():
            multi_freq = indiv_multi[concept]
            outfile.write("%s\t%s\t%d\t%d\n" % (year, concept, indiv_freq, multi_freq ) )
        with open(output_file+".total", "w") as outfile_total:
            outfile_total.write("%s\t%d\t%d\t%d\n" % (year, len(total_unique_concepts), nb_docs, total_multi_concepts) )
        
