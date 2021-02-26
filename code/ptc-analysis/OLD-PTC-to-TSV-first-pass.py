import bioc
import sys
from os import listdir, mkdir
from os.path import isfile, join, isdir
from collections import defaultdict 
import copy

# OUTPUT FORMAT: <year> <pmid> <pmcid> <source file> 

MAX_DOCS_BY_FILE = 50000
MEDPMC_CATEGORIES = ["filtered-medline", "pmc-articles", "overlap-medline"]

def create_file_handle(output_dirname, year, index):
    filename = join(output_dirname, str(year)+"."+ "%05d" % (index) +".tsv" )
    print("DEBUG: creating '"+filename+"'",flush=True)
    f = open(filename,"w")
    return f


if len(sys.argv) != 3:
    raise ValueError('Args: <PTC input dir> <output dir>')
 
ptc_input_dir = sys.argv[1]
files = [f for f in listdir(ptc_input_dir) if isfile(join(ptc_input_dir, f))] 
output_dir = sys.argv[2]

if not isdir(output_dir):
    mkdir(output_dir)
for category in MEDPMC_CATEGORIES:
    mkdir(join(output_dir, category)) 

# docsPMC[doc_id] = tuple (L, filename) whre L is a list of ( pmid, year, title)
docsPMC = defaultdict(list) 
# docsMed[doc_id] = tuple (year, filename, title, pmcid)
docsMed = dict() 
# by_year[Y] = list of doc ids for PMC or Medline
by_year = defaultdict(list) 
# set for the special case of a PMC article matching several Medline abstracts (very few cases but they exist) 
multiMedCasesInPMC = set()


invalid_pmc_docs = 0
double_front = 0
undef_year = 0

for fileNo, filename in enumerate(files): 
    print("\rReading file "+str(fileNo)+" / "+str(len(files)),end="",flush=True)
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
                        undef_year += 1
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
                    invalid_pmc_docs += 1
                    if pmid is None:
                        pmid="NOPMID"
                if pmcid is not None:
                    if pmcid != doc_id:
                        raise Exception("Invalid PMC document in file '"+filename+"', doc id '"+doc_id+"': document id does not match PMCID.")
                year = passage.infons.get('year')
                if year is None:
                    print("Warning: invalid PMC document in file '"+filename+"', doc id '"+doc_id+"':  year undefined, special year 0000 assigned.", file=sys.stderr,flush=True)
                    undef_year += 1
                    year = '0000'
                frontPmidYearList.append((pmid, year, text))
            elif (passage_type == 'abstract'):
                has_abstract = True
        if has_front:  # PMC
            if len(docsPMC[doc_id]) == 0:
                docsPMC[doc_id] = (copy.copy(frontPmidYearList), filename)   # shallow copy
                by_year[frontPmidYearList[0][1]].append(doc_id)
                for i in range(1,len(frontPmidYearList)):
                     multiMedCasesInPMC.add(frontPmidYearList[i][0])
            else:
                raise Exception("Error: two docs with same doc id "+doc_id+" (second one found in '"+filename+"')")
        else:
            if len(document.passages) == 2 and has_title and has_abstract: 
                if doc_id not in docsMed:
                    docsMed[doc_id] = (titleYear, filename, titleText, titlePmcid)
                    by_year[titleYear].append(doc_id)
            else:
                raise Exception("Invalid document in file '"+filename+"', doc id '"+doc_id+"': document has no front passage but doesn't satisfy Medline doc conditions either.")

print("\nRead "+str(len(files))+" files.")
print("Data summary: PMC docs =",len(docsPMC),", Medline docs =",len(docsMed),", dict 'by_year' contains ",len(by_year)," distinct years.",flush=True,end='')
print("Info: found "+str(invalid_pmc_docs)+" PMC documents with invalid PMID and/or PMCID")
print("Info: found "+str(undef_year)+" PMC or Medline documents with year undefined.")



for year, doc_ids in by_year.items():
    print("Writing PMC output files for year '"+str(year)+"': "+str(len(doc_ids))+" documents.",flush=True)
#    print("\rWriting output files for year '"+str(year)+"': "+str(len(doc_ids))+" documents.",end="")
    nb_docs = {}
    year_sub_index = {}
    current_files = {}
    for category in MEDPMC_CATEGORIES:
        nb_docs[category] = 0
        year_sub_index[category] = 0
        current_files[category] = create_file_handle(join(output_dir, category), year, year_sub_index[category])
    for doc_id in doc_ids:
#        print("DEBUG doc id ",doc_id,flush=True)
        pmcDoc = docsPMC.get(doc_id)
        medlineDoc = docsMed.get(doc_id)
        #
        # Things get tricky around here:
        #   - a PMC doc always has its pmcid as doc id
        #   - a single Medline doc has its pmid as doc id
        #   - a Medline doc which has the same doc id as a PMC has the pmcid as doc id, and its pmid can be found in the PMC doc
        #
        # If a PMC matches several Medline, then the first Medline follows case 3 above but the others follow case 2 (nothing is simple)
        #
        if pmcDoc is None and medlineDoc is None:
            raise Exception("Bug: no doc at all with doc id '"+doc_id+"'")
        elif pmcDoc is None and medlineDoc is not None:  # only Medline
            if doc_id not in multiMedCasesInPMC:  # avoid special case of multiple Medline matching a PMC
                     current_files["filtered-medline"].write("%s\t%s\t%s\t%s\n" % (year, doc_id, "_", medlineDoc[1]) )
                     nb_docs["filtered-medline"] += 1
        elif pmcDoc is not None and medlineDoc is None: # only PMC
            print("Warning: article ",doc_id," (file ",pmcDoc[1],") only in PMC", file=sys.stderr,flush=True)
            if len(pmcDoc[0])>1:
                print("Warning: article ",doc_id," (file ",pmcDoc[1],") has more than 1 'front' entry, writing only first.", file=sys.stderr,flush=True)
            current_files["pmc-articles"].write("%s\t%s\t%s\t%s\n" % (year, pmcDoc[0][0][0], doc_id, pmcDoc[0][0][1]) )
            nb_docs["pmc-articles"] += 1
        else:  # both
            print("DEBUG BOTH",file=sys.stderr,flush=True)
            print(pmcDoc,file=sys.stderr,flush=True)
            print(medlineDoc,file=sys.stderr,flush=True)
            # checking that the year is identical
            if pmcDoc[0][0][1] != medlineDoc[0]:
                print("Warning: the year is different between the Medline ("+medlineDoc[0]+") and PMC document ("+pmcDoc[0][0][1]+") for doc id '"+doc_id+"' (files "+pmcDoc[1]+" and "+medlineDoc[1]+")", file=sys.stderr,flush=True)
            current_files["pmc-articles"].write("%s\t%s\t%s\t%s\n" % (year, pmcDoc[0][0][0], doc_id, pmcDoc[1]) )
            nb_docs["pmc-articles"] += 1
            current_files["overlap-medline"].write("%s\t%s\t%s\t%s\n" % (year, pmcDoc[0][0][0], doc_id, medlineDoc[1]) )
            nb_docs["overlap-medline"] += 1
            if len(pmcDoc[0])>1:
                print("Warning: PMC doc "+doc_id+"' (file "+pmcDoc[1]+") contains multiple Medline matches.")
                for i in range(1,len(pmcDoc[0])):
                    thisMedDoc = docsMed[pmcDoc[0][i][0]] # get the corresponding medline doc in order to catch the file
                    if thisMedDoc is not None:
                        if pmcDoc[0][i][1] != thisMedDoc[0]:
                            print("Warning: [multi] the year is different between the Medline ("+thisMedDoc[0]+") and PMC document ("+pmcDoc[0][i][1]+") for doc id '"+doc_id+"' (files "+pmcDoc[1]+" and "+thisMedDoc[1]+")", file=sys.stderr,flush=True)
                        current_files["overlap-medline"].write("%s\t%s\t%s\t%s\n" % (pmcDoc[0][i][1], pmcDoc[0][i][0], doc_id, thisMedDoc[1]) )
                        nb_docs["overlap-medline"] += 1
                    else:
                        print("Warning: Multi-Medline PMC doc "+doc_id+"' (file "+pmcDoc[1]+") contains pmid "+pmcDoc[0][i][0]+" which was not found in Medline docs.")
        for category in MEDPMC_CATEGORIES:
            if nb_docs[category] >= MAX_DOCS_BY_FILE:
                current_files[category].close()
                year_sub_index[category] += 1
                current_files[category] = create_file_handle(join(output_dir, category), year, year_sub_index[category])
                nb_docs[category] = 0
    for category in MEDPMC_CATEGORIES:
        current_files[category].close()
print("\n",end="",flush=True)
