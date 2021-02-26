import bioc
import sys

if len(sys.argv) != 2:
    raise ValueError('Arg: filename.')
 
filename = sys.argv[1]
print(f'Filename is {filename}')
 
 
# read from a file
reader = bioc.BioCXMLDocumentReader(filename)
collection_info = reader.get_collection_info()
for document in reader:
    print("DOCUMENT "+str(document.id)+ " - infons: "+str(len(document.infons))+" - annotations: "+str(len(document.annotations))+" - relations: "+str(len(document.relations)))
    for infoKey, infoVal in document.infons.items():
        print("    DOCUMENT INFONS: "+infoKey+" -> "+infoVal)
    for annot in document.annotations:
        print("    DOCUMENT ANNOTATION:", end =" ")
        print(annot)
    for passage in document.passages:
        print("  PASSAGE: offset: "+str(passage.offset)+" - sentences: "+str(len(passage.sentences))+" - infons: "+str(len(passage.infons))+" - annotations: "+str(len(passage.annotations))+" - relations: "+str(len(passage.relations)))
        for infoKey, infoVal in passage.infons.items():
            print("    PASSAGE INFONS: "+infoKey+" -> "+infoVal)
        print("    PASSAGE TEXT: "+passage.text)
        for annot in passage.annotations:
            print("    PASSAGE ANNOTATION:", end =" ")
            print(annot)
            #for annotKey, annotVal in annot.items():
            #    print(annotKey+" -> "+annotVal)
            
