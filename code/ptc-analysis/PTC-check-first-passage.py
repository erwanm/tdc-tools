import bioc
import sys
from os import listdir, mkdir
from os.path import isfile, join, isdir
from collections import defaultdict 
import copy



if len(sys.argv) != 2:
    raise ValueError('Args: <PTC input dir>')
 
ptc_input_dir = sys.argv[1]
files = [f for f in listdir(ptc_input_dir) if isfile(join(ptc_input_dir, f))] 


med = 0
pmc = 0
for fileNo, filename in enumerate(files): 
    print("\rReading file "+str(fileNo)+" / "+str(len(files)),end="",flush=True,file=sys.stderr)
    reader = bioc.BioCXMLDocumentReader(join(ptc_input_dir, filename))
    # collection_info = reader.get_collection_info()
    
    for document in reader:
        passage_type = document.passages[0].infons.get('type')
        if passage_type == 'title':
            med += 1
        elif passage_type == 'front':
            pmc += 1
        else:
            raise Exception("Check failed: doc "+document.id+" in file "+filename+" has first passage which is neither 'title' or 'front'")
print("",file=sys.stderr)
print("Med docs:",med)
print("PMC docs;", pmc)
