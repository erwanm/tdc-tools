#!/usr/bin/env python3

from os.path import isfile, join, isdir
from collections import defaultdict 
import sys, getopt
import xml.etree.ElementTree as ET


PROG_NAME = "parse-mesh-desc-xml.py"

OUTPUT_SEP_TREE_IDS = " "

def usage(out):
    print("Usage: "+PROG_NAME+" [options] <Mesh desc20XX.xml> <output file>",file=out)
    print("",file=out)
    print("  Parses the file desc*.xml and writes a simpliied list of Mesh descriptors with their",file=out)
    print("  term and list of tree id positions. The output format is:",file=out)
    print("    <Mesh desc> <term> <space separated list of Mesh tree positions>",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out) 
    print("",file=out)



# main

umlsGroupFile = None
try:
    opts, args = getopt.getopt(sys.argv[1:],"hi")
except getopt.GetoptError:
    usage(sys.stderr)
    sys.exit(2)
for opt, arg in opts:
    if opt == "-h":
        usage(sys.stdout)
        sys.exit()
#    elif opt == "-i":
#        INPUT_COL_CONCEPT_ID = int(arg) -1

#print("debug args after options: ",args)

if len(args) != 2:
    usage(sys.stderr)
    sys.exit(2)

meshDescFile = args[0]
output_file = args[1]

tree = ET.parse(meshDescFile)
root = tree.getroot()

with open(output_file, "w") as outfile:
    for desc_node in root.findall('./DescriptorRecord'):
        mesh = desc_node.find('./DescriptorUI').text
        name = desc_node.find('./DescriptorName/String').text
        tree_id_nodes = desc_node.findall('./TreeNumberList/TreeNumber')
        tree_ids = OUTPUT_SEP_TREE_IDS.join([ n.text for n in  tree_id_nodes ])
        #print("DEBUG: ", mesh, name, tree_ids)
        outfile.write("%s\t%s\t%s\n" % (mesh, name, tree_ids) )
        #    print("")
        #    for child in desc_node:
        #        print("  DEBUG: ",child)
        #        print("  tag=",child.tag, "text =",child.text, "attribs=")
        #        for k,v in child.attrib.items():
        #            print(" %s=%v" % (k,v) )
        #        for grandchild in child:
        #            print("    tag=",child.tag, "text =",child.text, "attribs=")
        #            for k,v in child.attrib.items():
        #                print(" %s=%v" % (k,v) )

