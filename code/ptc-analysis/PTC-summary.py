import bioc
import sys
from os import listdir, mkdir
from os.path import isfile, join, isdir
from collections import defaultdict 
import copy

# OUTPUT FORMAT: 
# 1) <DOC ID> <MED> <FILE> <YEAR> <TITLE> <PMCID>
# 2) <DOC ID> <PMC> <FILE> <YEAR> <TITLE> <PMID> (one for each medline doc if multiple)



if len(sys.argv) != 2:
    raise ValueError('Args: <PTC input dir>')
 
ptc_input_dir = sys.argv[1]
files = [f for f in listdir(ptc_input_dir) if isfile(join(ptc_input_dir, f))] 


for fileNo, filename in enumerate(files): 
    print("\rReading file "+str(fileNo)+" / "+str(len(files)),end="",flush=True,file=sys.stderr)
    reader = bioc.BioCXMLDocumentReader(join(ptc_input_dir, filename))
    # collection_info = reader.get_collection_info()
    
    for document in reader:
        doc_id = document.id
#        print('DEBUG DOC '+doc_id)
        has_abstract = False
        has_front=  False
        has_title = False
        frontPmidYearList = []
        titleYear = None
        titleText = None
        titlePmcid = None
        for passage in document.passages:
            passage_type = passage.infons.get('type')
            if (passage_type == 'title'):
                has_title = True
                if not has_front:   # a PMC doc can have a 'title' passage (with no year), so if the doc already has 'front' passage, don't overwrite the year 
                    titleText = passage.text
                    titleYear = passage.infons.get('year')
                    if titleYear is None:
                        print("Warning: invalid Medline document in file '"+filename+"', doc id '"+doc_id+"':  year undefined, special year 0000 assigned.", file=sys.stderr,flush=True)
                        titleYear = '0000'
                    titlePmcid = passage.infons.get('article-id_pmc')
                    if titlePmcid is None:
                        titlePmcid = "_"
            elif (passage_type == 'front'):
                has_front = True
                text = passage.text
                pmid = passage.infons.get('article-id_pmid')
                pmcid = passage.infons.get('article-id_pmc')
                if pmid is None or pmcid is None:
                    print("Warning: invalid PMC document in file '"+filename+"', doc id '"+doc_id+"':  PMID and/or PMCID undefined.", file=sys.stderr,flush=True)
                    if pmid is None:
                        pmid="NOPMID"
                if pmcid is not None:
                    if pmcid != doc_id:
                        raise Exception("Invalid PMC document in file '"+filename+"', doc id '"+doc_id+"': document id does not match PMCID.")
                year = passage.infons.get('year')
                if year is None:
                    print("Warning: invalid PMC document in file '"+filename+"', doc id '"+doc_id+"':  year undefined, special year 0000 assigned.", file=sys.stderr,flush=True)
                    year = '0000'
                frontPmidYearList.append((pmid, year, text))
            elif (passage_type == 'abstract'):
                has_abstract = True
        if has_front:  # PMC
            for pmid, year, text in frontPmidYearList:
                print(doc_id+"\tPMC\t"+filename+"\t"+str(year)+"\t"+text+"\t"+pmid)
        else:
            if len(document.passages) == 2 and has_title and has_abstract: 
                print(doc_id+"\tMED\t"+filename+"\t"+str(titleYear)+"\t"+titleText+"\t"+titlePmcid)
            else:
                raise Exception("Invalid document in file '"+filename+"', doc id '"+doc_id+"': document has no front passage but doesn't satisfy Medline doc conditions either.")

