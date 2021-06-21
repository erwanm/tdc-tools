#!/usr/bin/env python3

#import sys
#from os import listdir, mkdir
from os.path import isfile, join, isdir
from collections import defaultdict 
#import copy
#import spacy
#import scispacy
import sys, getopt


PROG_NAME = "add-term-from-umls.py"

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

UMLS_STY_COL_CUI = 0
UMLS_STY_COL_TYPE_ID = 1 
UMLS_STY_COL_TYPE_TREE_ID = 2 
UMLS_STY_COL_TYPE_NAME = 3 

SEMGROUPS_COL_COARSE_GROUP_ID = 0
SEMGROUPS_COL_FINE_GROUP_ID = 2

UMLS_SEP = '|'
UMLS_MAIN_FILE = "MRCONSO.RRF"
UMLS_GROUP_FILE = "MRSTY.RRF"

FILTER_LANG = False
ADD_GROUP_COL = False
PTC_INPUT = False
USE_MESH_IDS = False
USE_PTC_AS_GROUP_COL = False

INPUT_CONCEPT_FREQ_SEP=":"
SEPARATOR_CONCEPT_ID_TYPE = "@"
OUTPUT_GROUP_SEP=" "


def usage(out):
    print("Usage: ls <input files> | "+PROG_NAME+" [options] <UMLS dir> <output suffix> ",file=out)
    print("",file=out)
    print("  Reads a list of input tsv files with a concept id column (either a UMLS CUI id or a Mesh id)",file=out)
    print("  and maps the id to a term using the UMLS data. For each input file <f> an output file ",file=out)
    print("  <f><output suffix> is created with an additional term column. ",file=out)
    print("  <UMLS dir> is the UMLS metathesaurus data, it must contain RRF files: <UMLS dir>/META/*.RRF",file=out)
    print("  Notes:",file=out)
    print("    - If no term is found for a concept, the term column contains 'NA'.",file=out)
    print("    - In case -g/-G is used, the group column contains a list of groups separated by '"+OUTPUT_GROUP_SEP+"'",file=out)
    print("      The list can be empty, in which case the group column is empty.",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
    print("    -i <id col>: concept id col; default: "+str(INPUT_COL_CONCEPT_ID)+".",file=out)
    print("    -m Mesh ids instead of default UMLS CUI ids (CUI is the default).",  file=out)
    print("    -p PTC input: the concept is represented as <id>@<category>, and a Mesh id has a ",file=out)
    print("       prefix 'MESH:'. Both the category and the prefix are removed. Implies '-m'.",file=out)
    print("    -g <UMLS sem groups file> add 'semantic group' column using UMLS group hierarchy which",file=out)
    print("       can be downloaded at https://lhncbc.nlm.nih.gov/semanticnetwork/download/SemGroups.txt",file=out)
    print("    -G add 'semantic group' column using PTC annotated type (requires PTC input; implies -p and -m)",file=out)
    print("    -l filter only English language terms. This can be produce 'NA' terms if a concept does ",file=out)
    print("       not have any English term (this is rare but it happens). By default English is prefered")
    print("       but non-English is used if no English term is found.",file=out)
    print("",file=out)



# main

umlsGroupFile = None
try:
    opts, args = getopt.getopt(sys.argv[1:],"hi:mpg:Gl")
except getopt.GetoptError:
    usage(sys.stderr)
    sys.exit(2)
for opt, arg in opts:
    if opt == "-h":
        usage(sys.stdout)
        sys.exit()
    elif opt == "-i":
        INPUT_COL_CONCEPT_ID = int(arg) -1
    elif opt == "-m":
        USE_MESH_IDS = True
    elif opt == '-p':
        PTC_INPUT = True
        USE_MESH_IDS = True
    elif opt == '-g':
        ADD_GROUP_COL = True
        umlsGroupFile = arg
    elif opt == '-G':
        ADD_GROUP_COL = True
        PTC_INPUT = True
        USE_MESH_IDS = True
        USE_PTC_AS_GROUP_COL = True
    elif opt == '-l':
        FILTER_LANG = True

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
umls_mesh_to_cui = defaultdict(list)

#
# due to the possibility that a concept doesn't have an English term, 
# there are two maps: one for English (index 1) one for non-English (index 0)
umls_cui_prefered_term = [ {}, {} ]

f= join(umlsDir, "META", UMLS_MAIN_FILE)
with open(f) as infile:
    for line in infile:
        cols = line.rstrip().split(UMLS_SEP)
        index_lang = 0
        if cols[UMLS_COL_LANG] in UMLS_LANG_FILTER_VAL:
            index_lang = 1
        if not FILTER_LANG or (index_lang == 1):                                     # filter language
            cui = cols[UMLS_COL_CUI]
            if cols[UMLS_COL_PREFERED] == 'Y' and umls_cui_prefered_term[index_lang].get(cui) is None:  # store only if prefered term, and only first found 
                umls_cui_prefered_term[index_lang][cui] = cols[UMLS_COL_TERM]
            if USE_MESH_IDS and cols[UMLS_COL_SOURCE] == UMLS_MESH_SOURCE_FILTER_VAL:       # store all the CUIs corresponding to this Mesh
                umls_mesh_to_cui[cols[UMLS_COL_MESH_ID]].append(cui)
#                if cols[UMLS_COL_MESH_ID] == 'D000690':
#                    print("DEBUG: ",cols[UMLS_COL_MESH_ID],":",cui, " - term = ",cols[UMLS_COL_TERM])

umls_group_fine_to_coarse = {}
groups_by_cui = defaultdict(set)
if umlsGroupFile is not None:
    print("INFO: Reading UMLS groups...")
    with open(umlsGroupFile) as infile:
        for line in infile:
            cols = line.rstrip().split(UMLS_SEP)
            umls_group_fine_to_coarse[cols[SEMGROUPS_COL_FINE_GROUP_ID]] = cols[SEMGROUPS_COL_COARSE_GROUP_ID]
    f= join(umlsDir, "META", UMLS_GROUP_FILE)
    with open(f) as infile:
        for line in infile:
            cols = line.rstrip().split(UMLS_SEP)
            cui = cols[UMLS_STY_COL_CUI]
            fine_group = cols[UMLS_STY_COL_TYPE_ID]
            coarse_group = umls_group_fine_to_coarse[fine_group]
            if coarse_group is None:                # sanity check
                raise Exception("Error: cannot find coarse group corresponding to fine group '"+fine_group+"'")
            groups_by_cui[cui].add(coarse_group)


print("INFO: Processing input files...")
for input_file in input_files:
    with open(input_file+outputSuffix,"w") as outfile:
        with open(input_file) as infile:
            for line in infile:
                cols = line.rstrip().split('\t')
                concept_id = cols[INPUT_COL_CONCEPT_ID]
                if PTC_INPUT:
                    sep_pos = concept_id.rfind(SEPARATOR_CONCEPT_ID_TYPE)
                    if sep_pos != -1:
                        ptc_category = concept_id[sep_pos+1:]
                        concept_id = concept_id[0:sep_pos]
                    else:
                        raise Exception("let's see:",concept_id)
                    if concept_id[:5] == 'MESH:':
                        is_mesh = True
                        concept_id = concept_id[5:]
                    else:
                        is_mesh = False
                    cols[INPUT_COL_CONCEPT_ID] = concept_id
                if USE_MESH_IDS:
                    cui_list = umls_mesh_to_cui[concept_id]
                    if len(cui_list)>0:
                        # just picking the first matched cui
                        cui = cui_list[0]
                else:
                    cui = concept_id
                term = umls_cui_prefered_term[1].get(cui)
                if term is None:
                    # second attempt if no match found in English: non-English version
                    term = umls_cui_prefered_term[0].get(cui)
                    if term is None:
                        if not PTC_INPUT or is_mesh:
                            print("Warning: no term found for concept '"+concept_id+"'",file=sys.stderr)
                        term = "NA"
                cols.append(term)
                if ADD_GROUP_COL:
                    groups = []
                    if USE_MESH_IDS:
                        if USE_PTC_AS_GROUP_COL:
                            if ptc_category is not None:
                                groups = [ ptc_category ]
                        else:
                            if cui_list is not None and len(cui_list)>0:
                                groups_set = set()
                                for cui in cui_list:
                                    for g in groups_by_cui[cui]:
                                        groups_set.add(g)
                                groups = list(groups_set)
                    else:
                        groups = groups_by_cui[concept_id]
                    cols.append(OUTPUT_GROUP_SEP.join(groups))
                outfile.write("\t".join(cols)+"\n")


