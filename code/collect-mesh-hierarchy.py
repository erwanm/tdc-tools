#!/usr/bin/env python3

#import sys
#from os import listdir, mkdir
from os.path import isfile, join, isdir
from collections import defaultdict 
#import copy
#import spacy
#import scispacy
import sys, getopt
import xml.etree.ElementTree as ET


PROG_NAME = "collect-mesh-hierarchy.py"

# all columns values are zero-indexed


ORIGINAL_MESH_XML = False
REVERSE_MODE = False
MAX_DEPTH = None
INPUT_AS_TREE_IDS = False
EXTEND_TO_OTHER_BRANCHES = False

def usage(out):
    print("Usage: cat <concepts> | "+PROG_NAME+" [options] <MeSH data> <output file> ",file=out)
    print("",file=out)
    print("  Reads a list of MeSH descriptors concepts (one by line) from STDIN and extracts the",file=out)
    print("  'descendants' according to the MeSH hierarchy. ",file=out)
    print("  <Mesh data> is either  the output file from parse-mesh-desc-xml.py or the orginal ",file=out)
    print("  MeSH file 'desc20XX.xml' if option '-x' is supplied. ",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
    print("    -x: read the original MeSH xml desc20XX.xml as first argument",file=out)
    print("    -r: reverse mode: collect all the ancestors of the concepts.",file=out)
    print("    -d <depth>: Maximum depth level of the search.",file=out)
    print("    -i: the input read from STDIN is made of MeSH tree ids instead of descriptors.",file=out)
    print("    -e: extend to other branches when a descendant descriptors appears in multiple branches",file=out)
    print("",file=out)


def add_to_tree(tree, mesh, tree_ids):
    for tree_id in tree_ids:
        parts = tree_id.split('.')
        prefix = parts[0:-1]
        child = parts[-1]
        if tree[prefix].get(child) is not None:
            raise Exception("Error: a MeSH tree id is supposed to correspond to a single MeSH descriptor (id: "+tree_id+", descriptors:"+tree[prefix][child]+","+mesh+")")
        tree[prefix][child] = mesh




# main

try:
    opts, args = getopt.getopt(sys.argv[1:],"hxrd:ie")
except getopt.GetoptError:
    usage(sys.stderr)
    sys.exit(2)
for opt, arg in opts:
    if opt == "-h":
        usage(sys.stdout)
        sys.exit()
    elif opt = "-x":
        ORIGINAL_MESH_XML = True
    elif opt == "-r":
        REVERSE_MODE = True
    elif opt == '-d':
        MAX_DEPTH = int(arg)
    elif opt == '-i':
        INPUT_AS_TREE_IDS = True
    elif opt == '-e':
        EXTEND_TO_OTHER_BRANCHES = True

#print("debug args after options: ",args)

if len(args) != 2:
    usage(sys.stderr)
    sys.exit(2)

mesh_data = args[0]
output_file = args[1]


# by_desc[mesh_descr] = ( term, tree_ids ) with tree_ids a list
by_desc = dict()

# the tree id is decomposed into a prefix, e.g. A02.633.567, and a single 'child' node id  e.g. 050
# tree[prefix][child] =  mesh_descr
tree = defaultdict(dict)

if ORIGINAL_MESH_XML:
    tree = ET.parse(mesh_data)
    root = tree.getroot()
    for desc_node in root.findall('./DescriptorRecord'):
        mesh = desc_node.find('./DescriptorUI').text
        name = desc_node.find('./DescriptorName/String').text
        tree_id_nodes = desc_node.findall('./TreeNumberList/TreeNumber')
        tree_ids = [ n.text for n in  tree_id_nodes ]
        by_desc[mesh] = (name, tree_ids)
        add_to_tree(tree, mesh, tree_ids)
else:
    with open(mesh_data) as infile:
        for line in infile:
            cols = line.rstrip().split('\t')
            mesh = cols[0]
            name = cols[1]
            tree_ids = cols[2].split(' ')
            by_desc[mesh] = (name, tree_ids)
            add_to_tree(tree, mesh, name, tree_ids)
 

# first get tree ids for input descriptors (or tree ids)
# and collect all corresponding descriptors depending on options
collected = defaultdict(set)
descrs = set([ s.rstrip() for s in sys.stdin ])
if INPUT_AS_TREE_IDS:
    current = descrs
else:
    current = set([ by_desc[mesh][1] for mesh in descrs ])
for tree_id in current:
    parts = tree_id.split('.')
    prefix = parts[0:-1]
    child = parts[-1]
    mesh = tree[prefix][child]
    collected[mesh].add(tree_id)
                

depth = 1
while len(current)>0 and (MAX_DEPTH is None or depth <= MAX_DEPTH):
    new_ids = set()
    for prefix in current:
        if REVERSE_MODE:
            parts = prefix.split('.')
            if len(parts)>1:
                new_prefix = parts[0:-1]
                mesh = tree[new_prefix]
                collected[mesh].add(new_prefix)
                new_ids.add(new_prefix)
                if EXTEND_TO_OTHER_BRANCHES:
                    new_ids.union(set(by_desc[mesh][1]))
        else:
            for child,mesh in tree[prefix].items():
                tree_id = prefix+"."+child
                collected[mesh].add(tree_id)
                new_ids.add(tree_id)
                if EXTEND_TO_OTHER_BRANCHES:
                    new_ids.union(set(by_desc[mesh][1]))
    current = new_ids
    depth += 1


with open(output_file,"w") as outfile:
    for mesh, tree_ids in collected.items():
        outfile.write(mesh+"\t"+by_desc[mesh][0]+"\t"+" ".join(tree_ids)+"\n")


