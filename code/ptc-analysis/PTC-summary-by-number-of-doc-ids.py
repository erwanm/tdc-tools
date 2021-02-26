import sys
from os import listdir, mkdir
from os.path import isfile, join, isdir
from collections import defaultdict 
import copy

# OUTPUT FORMAT: 
# 1) <DOC ID> <MED> <FILE> <YEAR> <TITLE> <PMCID>
# 2) <DOC ID> <PMC> <FILE> <YEAR> <TITLE> <PMID> (one for each medline doc if multiple)



if len(sys.argv) != 3:
    raise ValueError("Args: <PTC 'new summary' file> <output prefix>")
 
ptc_input_file = sys.argv[1]
output_prefix =  sys.argv[2]


docs = defaultdict(list)

with open(ptc_input_file, "r") as f:
    for line in f: 
        values = line.strip().split('\t')
        docs[values[0]].append(values)

f1 = open(output_prefix+".1.tsv", "w")
f2 = open(output_prefix+".2.tsv", "w")
fmore = open(output_prefix+".more.tsv", "w")

single=0
two=0
more=0
med_with_pmcid = 0
med_with_pmcid_equal_doc_id = 0
med_with_pmcid_in_docs = 0
pmc_with_pmid_in_docs = 0
same_title = 0
same_year = 0
same_both = 0
one_med_one_pmc = 0
for doc_id, l in docs.items():
    if len(l) == 1:
        single += 1
        x = l[0]
        f1.write("\t".join(x)+"\n")
    elif len(l) == 2:
        two += 1
        for x in l:
            f2.write("\t".join(x)+"\n")
    else:
        more+=1
        for x in l:
            fmore.write("\t".join(x)+"\n")
    has_med = False
    has_pmc = False
    titles = set()
    years = set()
    for x in l:
        years.add(x[2])
        titles.add(x[3])
        if x[1] == "MED":
            has_med = True
            if x[5] != "_":  # has PMCID
                med_with_pmcid += 1
                id_no = x[5][3:]
                if doc_id == id_no:
                    med_with_pmcid_equal_doc_id += 1
                if docs.get(id_no) is not None:
                    med_with_pmcid_in_docs += 1
        elif x[1] == "PMC":
            has_pmc = True
            if docs.get(x[5]) is not None:  # pmid
                pmc_with_pmid_in_docs += 1
        else:
            raise Exception("bug")
    if len(l)==2 and has_med and has_pmc:
        one_med_one_pmc += 1
        if len(titles) == 1:
            same_title += 1
            if len(years) == 1:
                same_year += 1
                same_both += 1
        elif len(years) == 1:
              same_year += 1
        
f1.close()
f2.close()
fmore.close()

print("Cases unique doc id:",single)
print("Cases doc id has 2 docs:",two)
print("  with one med and one PMC:",one_med_one_pmc)
print("    same year:", same_year)
print("    same title:", same_title)
print("    same both:", same_both)
print("Cases doc id has more than 2 docs:",more)
print("")
print("Med doc with PMCID:",med_with_pmcid)
print("  with PMCID equal to doc id:",med_with_pmcid_equal_doc_id)
print("  with PMCID in docs:",med_with_pmcid_equal_doc_id)
print("PMC doc with PMID in docs:", pmc_with_pmid_in_docs)
