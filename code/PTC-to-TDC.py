import bioc
import sys
from os import listdir, mkdir
from os.path import isfile, join, isdir
from collections import defaultdict 
import copy
import spacy
import scispacy



MAX_DOCS_BY_FILE = 10000
MEDPMC_CATEGORIES = ["filtered-medline", "pmc-articles", "pmc-abstracts"]
SEPARATOR_CONCEPT_ID_TYPE = "@"

# init scispacy model
nlp = spacy.load("en_core_sci_sm")


def create_file_handles(output_dirname, year, index):
    res = []
    for ext in [ "raw", "tok", "cuis" ]:
        filename = join(output_dirname, str(year)+"."+ "%05d" % (index) +"." + ext )
#        print("DEBUG: creating '"+filename+"'",flush=True)
        f = open(filename,"w")
        res.append(f)
    return res


#
# calculate the sent index and offset in this sentence corresponding to the source offset based on the document
#
def map_passage_offset(ptc_offset, sentences):
    if len(sentences) == 0:
        raise Exception("Bug: cannot find annotation in 0 sentences.")
    sent_no = 0
#    print("  DEBUG map_passage_offset: sent_no = ",sent_no,", sent length =",len(sentences[sent_no][1]),", sent offset =",sentences[sent_no][0],", target_offset =",ptc_offset)
    # second condition: while the target ptc_offset is farther than then end of the current sentence
    while sent_no < len(sentences) and ptc_offset >= sentences[sent_no][0]+len(sentences[sent_no][1]):
#        print("  DEBUG map_passage_offset: sent_no = ",sent_no,", sent length =",len(sentences[sent_no][1]),", sent offset =",sentences[sent_no][0],", target_offset =",ptc_offset)
        sent_no += 1
#    print("  DEBUG map_passage_offset STOP: sent_no = ",sent_no,", sent length =",len(sentences[sent_no][1]),", sent offset =",sentences[sent_no][0],", target_offset =",ptc_offset)
    if sent_no == len(sentences): # reached the last sentence and offset still further: error
            raise Exception("Bug: the position of the offset is too far.")
    # return the sentence id and the offset from the start of the sentence
    return (sent_no, ptc_offset - sentences[sent_no][0])
            

#
# merge sentences index and index+1 in the list of sentences
#
def merge_two_sentences(sentences, sent_no):
    if len(sentences) < sent_no+1:
        raise Exception("Bug: no sentence after sent_no "+str(sent_no)+", cannot merge with next sentence.")
    # we need to make sure the offsets stay consistent with the source offsets by adding spaces if needed:
    merged_sent = sentences[sent_no][1]
    if sentences[sent_no][0] + len(merged_sent) > sentences[sent_no +1][0]:
        raise Exception("Bug: sentence at sent_no "+str(sent_no)+" has offset ="+str(sentences[sent_no][0])+" and length ="+str(len(merged_sent))+" but the next sentence starts at offset "+str(sentences[sent_no+1][0])+".")
    while sentences[sent_no][0] + len(merged_sent) < sentences[sent_no +1][0]:
        merged_sent += " "
    # now the sentence is consistent with the offset, concatenate:
    merged_sent += sentences[sent_no+1][1]
    sentences[sent_no] = (sentences[sent_no][0], merged_sent)
    # remove the next sentence
    sentences.pop(sent_no+1)
        

#
# returns the Spacy Document
#
def extract_data_from_passage(pmid, year, partId, elemId, passage, files_triple_list, count, filename, doc_id):
    doc = nlp(passage.text)
#    print("DEBUG extract_data_from_passage. passage offset = ",passage.offset,"; length =",len(passage.text))
#    print(" FULL TEXT = ",passage.text)
    # sentences[sent_no] = (offset, sentence_text)
    sentences = []
    # 1)  iterate the sentences segmented by Spacy to store the offset and the sentence
    for sentNo,sentenceTokens in enumerate(list(doc.sents)):
        #  offset of the first token in the sentence
        offset = sentenceTokens[0].idx
#        print("  ", sentNo, " ; offset ="+str(offset)+" [doc: "+str(offset+passage.offset)+"] ; length = ",str(len(str(sentenceTokens)))+": ",sentenceTokens)
        # storing the offset FROM DOCUMENT START instead of passage start, because the annotations offsets are based on the document
        offset += passage.offset
        sentences.append((offset, str(sentenceTokens)))
    # passage_annotation[sent_no][posititon] = list of concepts at this position
    # remark: a position is supposed to have a single concept but there are a few exceptions in the data for which a warning is printed
    passage_annotations = defaultdict(lambda: defaultdict(list))
    # 2) iterate the PTC annotations and store them
    for annot in passage.annotations:
#        print("    DEBUG text =",annot.text)
#        print("    DEBUG infons =",annot.infons)
        if annot.infons.get("identifier") is None or annot.infons.get("identifier") == "-" :
            count["annot_without_identifier"] += 1
        else:
            count["annotations"] += 1
            if SEPARATOR_CONCEPT_ID_TYPE in annot.infons["identifier"]: # warning only (this case happens very rarely with '@' but there is at least one occurrence)
                print("Warning: the separator character '"+SEPARATOR_CONCEPT_ID_TYPE+"' is present in id '"+annot.infons["identifier"]+"'", file=sys.stderr)
            if SEPARATOR_CONCEPT_ID_TYPE in annot.infons["type"]:       # fatal error
                raise Exception("Bug: the separator character '"+SEPARATOR_CONCEPT_ID_TYPE+"' is present in type '"+annot.infons["type"]+"'")
            concept = annot.infons["identifier"] + SEPARATOR_CONCEPT_ID_TYPE + annot.infons["type"]
            for location in annot.locations:
                #            print("      DEBUG location =", location.offset,";",location.length)
                #            print("      TEST PASSAGE: ", ) # ok
                annot_content_from_passage = passage.text[location.offset -passage.offset:location.offset -passage.offset +location.length]
                sanity_check_ok = True
                if annot_content_from_passage != annot.text: # sanity check (not strictly necessary)
                    print("Warning: sanity check failed in doc '"+doc_id+"', file "+filename+": the annotation text '"+annot.text+"' and the text extracted at the provided location in the passage '"+annot_content_from_passage+"' don't match. Details: concept = '"+concept+"'; passage = '"+passage.text+"', location: offset = "+str(location.offset-passage.offset)+", length = "+str(location.length),file=sys.stderr)
                    count["sanity_check_against_PTC_text_failed"] += 1
                    sanity_check_ok = False
                # trying to get it as spacy sentence: 
                (sent_no, sent_offset) = map_passage_offset(location.offset, sentences)
                # possible problem: the annotation spans over two Spacy sentences
                while len(sentences[sent_no][1]) < sent_offset + location.length:
                    #                print("Warning: the annotation spans over two Spacy sentences, merging the two sentences.",file=sys.stderr)
                    count["merged_sentences"] += 1
                    merge_two_sentences(sentences, sent_no)
                    (sent_no, sent_offset) = map_passage_offset(location.offset, sentences)
                annot_content_from_my_sentences = sentences[sent_no][1][sent_offset:sent_offset+location.length]
                #            print("      TEST PASSAGE2: ", annot_content_from_my_sentences)
                # note: if the first sanity check failed, we don't do the second one as it apparently always fails
                if sanity_check_ok and annot_content_from_my_sentences != annot.text:  # important: check that the extracted term matches the term in the annotation 
                    print("Warning: sanity check failed in doc '"+doc_id+"', file "+filename+": the annotation text '"+annot.text+"' and the text extracted at the calculated location in the sentence '"+annot_content_from_passage+"' don't match.  Details: concept = '"+concept+"'; passage = '"+passage.text+"', location = "+str(location.offset-passage.offset),file=sys.stderr)
                    count["sanity_check_against_sentence_position_failed"] += 1
                # once everything ok, add to the list corresponding to the sentence in dict passage_annotations, index by sentence id and position
                cui_line = [ pmid, partId, str(elemId), str(sent_no), concept,  str(sent_offset), str(location.length) ]
                if passage_annotations[sent_no].get(sent_offset) is not None:
                    first_annot_concept = passage_annotations[sent_no][sent_offset][0][4]
                    first_annot_length = int(passage_annotations[sent_no][sent_offset][0][6])
                    first_annot_text = sentences[sent_no][1][sent_offset:sent_offset+first_annot_length]
                    print("Warning: two annotations at the same position in doc '"+doc_id+"', file "+filename+": first annotation for text '"+first_annot_text+"' (concept id '"+first_annot_concept+"'; length "+str(first_annot_length)+"); second annotation for text '"+annot_content_from_my_sentences+"' (concept id '"+concept+"'; length "+str(location.length)+")",file=sys.stderr)
                    count["multiple_annotations_same_position"] += 1
                # note: the annotations are written later in order to order them by their order in the text (not necessarily followed in PTC)
                passage_annotations[sent_no][sent_offset].append(cui_line)
    # the count of sentences and the writing of the .tok file is done after going through the annotations in order to account for merged sentences
    count["sentences"] += len(sentences)
    # .tok file
    for sent_no, sentencePair in enumerate(sentences):
        sentence = sentencePair[1]
        for files_triple in files_triple_list:
            files_triple[1].write("%s\t%s\t%s\t%s\t%d\t%s\n" % (pmid, year, partId, elemId, sent_no, sentence ) )
        # .cuis file
        for (_, cui_lines) in sorted(passage_annotations[sent_no].items()):
            for cui_line in cui_lines:
                line = "\t".join(cui_line)+"\n"
                for files_triple in files_triple_list:
                    files_triple[2].write(line)

def process_medline(doc, count, output_files, first_year, last_year, output_dir, filename):
    pmid = doc.id
    year = None
    title = None
    abstract = None
    for passage in doc.passages:
        passage_type = passage.infons.get('type')
        if passage_type == 'title':
            title = passage.text
            year = passage.infons.get('year')
            if year is None:
                count["med_undef_year"] += 1
                year = '0000'
        elif passage_type == 'abstract':
            abstract = passage.text
        else:
            raise Exception("Bug: a Medline document must have only 'title' and 'abstract' as passage.")
    if int(year) >= first_year and int(year) < last_year:
        count["medline"] += 1
        this_year_output = output_files["filtered-medline"].get(year)
        if this_year_output is None:
            this_year_output = (0, 0, create_file_handles(join(output_dir, "filtered-medline"), year, 0))
            output_files["filtered-medline"][year] = this_year_output
        if this_year_output[0] >= MAX_DOCS_BY_FILE:
            for f in this_year_output[2]:
                f.close()
            new_index = this_year_output[1] +1
            this_year_output = (0, new_index, create_file_handles(join(output_dir, "filtered-medline"), year, new_index) )
 #       print("DEBUG count = "+str(this_year_output_art[0]+1))
        output_files["filtered-medline"][year] = (this_year_output[0]+1, this_year_output[1], this_year_output[2])
        # .raw file
        this_year_output[2][0].write("%s\t%s\t%s\t%s\n" % (pmid, year, title, abstract) )
        # .tok and .cuis files
        extract_data_from_passage(pmid, year, "title",0, doc.passages[0], [ this_year_output[2] ], count, filename, doc.id)
        extract_data_from_passage(pmid, year, "abstract",0, doc.passages[1], [ this_year_output[2] ], count, filename, doc.id)


def process_pmc(doc, count, output_files, first_year, last_year, output_dir, filename):
    doc_id = doc.id
    year = None
    title = None
    if doc.passages[0].infons.get('type') != 'front':
        raise Exception("Bug: a PMC document must have 'front' as type for the first passage.")
    pmid = doc.passages[0].infons.get('article-id_pmid')
    pmcid = doc.passages[0].infons.get('article-id_pmc')
    if pmid is None or pmcid is None:
        count["invalid_pmc_docs"] += 1
        if pmid is None:
            pmid="NOPMID"
    if pmcid is not None:
        if pmcid != doc_id: # sanity check
            raise Exception("Invalid PMC document doc id '"+doc_id+"': document id does not match PMCID.")
    title = doc.passages[0].text
    year = doc.passages[0].infons.get('year')
    if year is None:
        count["pmc_undef_year"] += 1
        year = '0000'
    if int(year) >= first_year and int(year) < last_year:
        count["pmc"] += 1
        fullid = pmid + "." + pmcid
        this_year_output_art = output_files["pmc-articles"].get(year)
        this_year_output_abs = output_files["pmc-abstracts"].get(year)
        if this_year_output_art is None:  # note: both art and abs are None
            this_year_output_art = (0, 0, create_file_handles(join(output_dir, "pmc-articles"), year, 0))
            output_files["pmc-articles"][year] = this_year_output_art
            this_year_output_abs = (0, 0, create_file_handles(join(output_dir, "pmc-abstracts"), year, 0))
            output_files["pmc-abstracts"][year] = this_year_output_abs
        if this_year_output_art[0] >= MAX_DOCS_BY_FILE:  # both art and abs again
            for f in this_year_output_art[2]:
                f.close()
            for f in this_year_output_abs[2]:
                f.close()
            new_index = this_year_output_art[1] + 1
            this_year_output_art = ( 0, new_index, create_file_handles(join(output_dir, "pmc-articles" ), year, new_index) )
            this_year_output_abs = ( 0, new_index, create_file_handles(join(output_dir, "pmc-abstracts"), year, new_index) )
#        print("DEBUG count = "+str(this_year_output_art[0]+1))
        output_files["pmc-articles"][year] = ( this_year_output_art[0]+1, this_year_output_art[1], this_year_output_art[2] )
        output_files["pmc-abstracts"][year] = ( this_year_output_abs[0]+1, this_year_output_abs[1], this_year_output_abs[2] )
        # .tok and .cuis files
        full_content = []
        abstract = [1]
        undef_passage_type = False
        for passageNo, passage in enumerate(doc.passages):
            passage_type = passage.infons.get('section_type')
            # ignore a few special passage types: reference, acknowledgements, author contribution
            if (passage_type is None) or (passage_type != 'REF' and passage_type != 'ACK_FUND' and passage_type != 'AUTH_CONT'):
                if passage_type is None:
                    undef_passage_type = True
#                    print("Warning: no value for 'section_type' in doc id '"+doc_id+"'.", file=sys.stderr,flush=True)
                    passage_type = "STUFF" # this will be considered part of the article body
                if passage_type == 'TITLE':
                    extract_data_from_passage(fullid, year, "title", passageNo, passage, [this_year_output_abs[2], this_year_output_art[2]], count, filename, doc.id)
                elif passage_type == 'ABSTRACT':
                    abstract.append(passage.text)
                    extract_data_from_passage(fullid, year, "abstract", passageNo, passage, [this_year_output_abs[2], this_year_output_art[2]], count, filename, doc.id)
                else:  # any other passage type is considered part of the article body
                    full_content.append(passage.text)
                    extract_data_from_passage(fullid, year, passage_type, passageNo, passage, [this_year_output_art[2]], count, filename, doc.id)
        if undef_passage_type:
            count["pmc_contains_undef_passage_type"] += 1
        # .raw file
        this_year_output_abs[2][0].write("%s\t%s\t%s\t%s\n" % (pmid, year, title, abstract) )
        this_year_output_art[2][0].write("%s\t%s\t%s\t%s\t%s\n" % (pmid, year, title, abstract,  " . ".join(full_content)) )





# main

if len(sys.argv) != 3 and len(sys.argv) != 5:
    raise ValueError('Args: <PTC input dir> <output dir> [<min year> <max year>]')

ptc_input_dir = sys.argv[1]
files = [f for f in listdir(ptc_input_dir) if isfile(join(ptc_input_dir, f))] 
output_dir = sys.argv[2]
if len(sys.argv) == 5:
    first_year = int(sys.argv[3])
    last_year = int(sys.argv[4])
else:
    first_year = 0
    last_year = 3000

if not isdir(output_dir):
    mkdir(output_dir)
for category in MEDPMC_CATEGORIES:
    d = join(output_dir, category)
    if not isdir(d):
        mkdir(d) 

count = { "medline" : 0, "pmc" : 0, "invalid_pmc_docs" : 0, "med_undef_year" : 0, "pmc_undef_year" : 0, "sentences" : 0, "merged_sentences" : 0 , "annot_without_identifier" : 0, "annotations" : 0, "pmc_contains_undef_passage_type" : 0, "multiple_annotations_same_position" : 0, "sanity_check_against_sentence_position_failed" : 0, "sanity_check_against_PTC_text_failed": 0 }

# output_files[category][year] = ( current_nb_docs, current_index, triple_file_handles ) where triple_file_handles = ( raw_fh, tok_fh, cuis_fh )
output_files = {}
for cat in MEDPMC_CATEGORIES:
    output_files[cat] = {}

for fileNo, filename in enumerate(files): 
    print("\rReading file "+str(fileNo)+" / "+str(len(files)),end="",flush=True)
    reader = bioc.BioCXMLDocumentReader(join(ptc_input_dir, filename))
    
    for document in reader:
        if len(document.passages)==2 and document.passages[0].infons.get('type') == 'title' and document.passages[1].infons.get('type') == 'abstract':
            process_medline(document, count, output_files, first_year, last_year, output_dir, filename)
        elif document.passages[0].infons.get('type') == 'front':
            process_pmc(document, count, output_files, first_year, last_year, output_dir, filename)
        else:
            raise Exception("Check failed: doc "+document.id+" in file "+filename+" has first passage which is neither 'title' or 'front'")
print("")
for category in MEDPMC_CATEGORIES:
    for _,triple_file_output in output_files[category].items():
        for f in triple_file_output[2]:
            f.close()
for key, val in count.items():
    print("Info:", key, "=", val)
