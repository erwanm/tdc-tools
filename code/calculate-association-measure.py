#!/usr/bin/env python3

#import sys
import math

import sys, getopt


PROG_NAME = "calculate-association-measure.py"

available_measures = [ 'pmi', 'npmi', 'pmi2', 'pmi3', 'scp' ]
selected_measures = [ 'pmi' ]

def usage(out):
    print("Usage: "+PROG_NAME+" [options] <joint file> <indiv file> <totals file> <output file>",file=out)
    print("",file=out)
    print("  Reads the three folowing input files:",file=out)
    print("    - <joint file>: <concept1> <concept2> <freq>",file=out)
    print("    - <indiv file>: <concept> <freq> <multi-freq (unused)>",file=out)
    print("    - <totals file>: <total freq> <total multi-freq (unused)> (single line)",file=out)
    print("  These files can be generated using ptc-aggregate-across-types.py from the indiv and",file=out)
    print("  joint files by year (see TDC tools documentation).",file=out)
    print("  The association measure (PMI by default) is calculated for every pair in the joint",file=out)
    print("  file and the result is added as a fourth column in <output file>",file=out)
    print("",file=out)
    print("  Options",file=out)
    print("    -h: print this help message.",file=out)
    print("    -m <measures> comma-separated list of measures to calculate. Available:",",".join(available_measures),file=out)
    print("",file=out)



# returns an array of values corresponding to the measures ids in 'measures'
#
def calculate_measures(joint, indivA, indivB, total, measures):
    jointProb = joint / total
    pA = indivA / total
    pB = indivB / total
    pmi = math.log2( jointProb / (pA * pB) )
    res = []
    for m in measures:
        if m  == 'scp':
            res.append(jointProb ^ 2 / (pA * pB))
        elif m  == 'pmi':
            res.append(pmi)
        elif m  == 'npmi':
            res.append(- pmi / math.log2(jointProb))
        elif m == 'pmi2':
            res.append(math.log2( (jointProb^2) / (pA * pB) ))
        elif m == 'pmi3':
            res.append(math.log2( (jointProb^3) / (pA * pB) ))
    return res



# main

try:
    opts, args = getopt.getopt(sys.argv[1:],'hm:')
except getopt.GetoptError:
    usage(sys.stderr)
    sys.exit(2)
for opt, arg in opts:
    if opt == "-h":
        usage(sys.stdout)
        sys.exit()
    elif opt == "-m":
        selected_measures = arg.split(",")
        for m in selected_measures:
            if m not in available_measures:
                raise("Error, invalid measure id '"+m+"'. Available measures: "+",".join(available_measures))

#print("debug args after options: ",args)

if len(args) != 4:
    usage(sys.stderr)
    sys.exit(2)

joint_file = args[0]
indiv_file = args[1]
totals_file = args[2]
output_file = args[3]


total = None
with open(totals_file) as infile:
    for line in infile:
        cols = line.rstrip().split("\t")
        total = int(cols[0])


indiv = {}
with open(indiv_file) as infile:
    for line in infile:
        cols = line.rstrip().split("\t")
        indiv[cols[0]] = int(cols[1])
print("Info: read",len(indiv),"individual concepts.", file=sys.stderr)


with open(output_file,"w") as outfile:
    with open(joint_file) as infile:
        for line in infile:
            cols = line.rstrip().split("\t")
            c1 = cols[0]
            c2 = cols[1]
            joint = int(cols[2])
            out = calculate_measures(joint, indiv[c1], indiv[c2], total, selected_measures)
            out = [ c1, c2, str(joint) ] + [ str(x) for x in out ]
            outfile.write("%s\n" % ("\t".join(out)))
