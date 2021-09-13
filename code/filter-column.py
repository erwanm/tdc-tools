#!/usr/bin/env python3

#import sys
#from os import listdir, mkdir
from os.path import isfile, join, isdir
from collections import defaultdict 


import sys, getopt


PROG_NAME = "filter-column.py"

SEPARATOR_CONCEPT_ID_TYPE = "@"

def usage(out):
    print("Usage: cat <patterns> | "+PROG_NAME+" [options] <input file> <column no(s)>",file=out)
    print("",file=out)
    print("  Filters <input file> keeping only line where column <column no(s)> contains a value which ",file=out)
    print("  belongs to one of the <patterns> given on STDIN.",file=out)
    print("  <column no(s)> can contain several column numbers separated by comma. By default the",file=out)
    print("  <patterns> are expected to contain the same number of columns, and the matching is applied",file=out)
    print("  to all the target columns (i.e. a line is kept only if the exact same sequence of columns values",file=out)
    print("  appears in <patterns>). See also options.",file=out)
    print("",file=out)
    print("  Options")
    print("    -h: print this help message.",file=out)
    print("    -u union on multiple target columns: <patterns> interpreted as single column; a line matches if",file=out)
    print("       at least one column matches. No effect if a single target column is provided.",file=out)
    print("    -i intersection on multiple target columns: <patterns> interpreted as single column; a line matches",file=out)
    print("       if all the columns match. Incompatible with -u; no effect with single target column.",file=out)
    print("    -m numerical minimum: <patterns> contains either a single numerical value interpreted as a minimum",file=out)
    print("       threshold or two values interpreted as minimum and maximum.",file=out)
    print("    -M numerical maximum: <patterns> contains either a single numerical value interpreted as a maximum",file=out)
    print("       threshold or two values interpreted as minimum and maximum.",file=out)
    print("    -p PTC <concept>@<type> format in the target columns: ignore the type part, not present in targets.",file=out)
    print("",file=out)
    print("",file=out)


def condition_satisfied(values, patterns, mini, maxi, ptc_format):
#    print("DEBUG; val=",values,"; mini=",mini,"; maxi=",maxi,file=sys.stderr)
#    print("DEBUG patterns = ", patterns,file=sys.stderr)
    if mini is None and maxi is None:
        l = []
        if ptc_format:
            for val in values:
                sep_pos = val.rfind(SEPARATOR_CONCEPT_ID_TYPE)
                if sep_pos != -1:
                    #                ptc_category = concept[sep_pos+1:]
                    val = val[0:sep_pos]
                else:
                    print("Warning: PTC format separator not found in '"+val+"'",file=sys.stderr)
                l.append(val)
        else:
            l = values
        return '\t'.join(l) in patterns
    elif mini is not None and maxi is not None:
        return int(values[0])>=mini and int(values[0])<=maxi
    elif mini is not None:
        return int(values[0])>=mini
    elif maxi is not None:
        return int(values[0])<=maxi



# main

opt_union = False
opt_intersection = False
numerical_min = False
numerical_max = False
ptc_format = False
try:
    opts, args = getopt.getopt(sys.argv[1:],"huimMp")
except getopt.GetoptError:
    usage(sys.stderr)
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        usage(sys.stdout)
        sys.exit()
    if opt == '-u':
        opt_union = True
    if opt == '-i':
        opt_intersection = True
    if opt == '-m':
        numerical_min = True
    if opt == '-M':
        numerical_max = True
    if opt == "-p":
        ptc_format= True

if opt_union and opt_intersection:
    raise Exception("Error: incompatible options -u and -i")

if ptc_format and (numerical_min or numerical_max):
    raise Exception("Error: option -p not compatible with -m or -M")

# print("debug args after options: ",args)

if len(args) != 2:
    usage(sys.stderr)
    sys.exit(2)

inputFile=args[0]
colNos=[ int(c)-1 for c in args[1].split(',') ]


patterns=set()
#print("Reading patterns on STDIN...",file=sys.stderr)
line_no=1
for line in sys.stdin:
    val = line.rstrip()
    if numerical_min or numerical_max:
        for v in val.split():
            patterns.add(int(v))
    else:
        if not opt_union and not opt_intersection:
            n = len(val.split('\t'))
            if n != len(colNos):
                raise Exception("Error: expecting %d target columns but %d columns found in pattern at line %d: %s" % (len(colNos), n, line_no, val) )
        patterns.add(val)
    line_no+=1

minimum = None
maximum = None
if numerical_min or numerical_max:
    if len(patterns)>2:
        raise Exception("Error: numerical filtering (-m or -M) requires only one or two numerical values as STDIN.")
    if len(colNos)>1 and not opt_union and not opt_intersection:
        raise Exception("Error: numerical filtering with multiple columns requires -u or -i.")
    if len(patterns)==2:
        numerical_min = True
        numerical_max = True
    if  numerical_min:
        minimum = min(patterns)
    if numerical_max:
        maximum = max(patterns)


#print("Filtering input file...",file=sys.stderr)
with open(inputFile) as infile:
    for line in infile:
        cols = line.rstrip().split("\t")
        target_cols = [ cols[colNo] for colNo in colNos ]
        if opt_union:
            for col in target_cols:
                if condition_satisfied([col], patterns, minimum, maximum, ptc_format):
                    print(line,end='')
                    break
        elif opt_intersection:
            line_pass = True
            for col in target_cols:
                if not condition_satisfied([col], patterns, minimum, maximum, ptc_format):
                    line_pass = False
                    break
            if line_pass:
                print(line,end='')
        else:
            if condition_satisfied(target_cols, patterns, minimum, maximum, ptc_format):
                print(line,end='')

