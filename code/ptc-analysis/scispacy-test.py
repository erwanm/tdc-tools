import spacy
import scispacy

from scispacy.linking import EntityLinker

#print(spacy.__file__)
#print(scispacy.__file__)

nlp = spacy.load("en_core_sci_sm")

# This line takes a while, because we have to download ~1GB of data
# and load a large JSON file (the knowledge base). Be patient!
# Thankfully it should be faster after the first time you use it, because
# the downloads are cached.
# NOTE: The resolve_abbreviations parameter is optional, and requires that
# the AbbreviationDetector pipe has already been added to the pipeline. Adding
# the AbbreviationDetector pipe and setting resolve_abbreviations to True means
# that linking will only be performed on the long form of abbreviations.
nlp.add_pipe("scispacy_linker", config={"resolve_abbreviations": True, "name": "umls"})

doc = nlp("Spinal and bulbar muscular atrophy (SBMA) is an \
           inherited motor neuron disease caused by the expansion \
           of a polyglutamine tract within the androgen receptor (AR). \
           SBMA can be caused by this easily.")

print(type(doc))

sentences = list(doc.sents)
print(len(sentences)," sentences")

for sentNo,sent in enumerate(sentences):
    print("Sentence ",sentNo,": ")
    for tokNo, token in enumerate(sent):
        print("  token ",tokNo,": '"+str(token)+"'")


linker = nlp.get_pipe("scispacy_linker")

for entNo, entity in enumerate(doc.ents):
    print("Entity",entNo,":", entity, type(entity))
    print('  start=',entity.start,'; end=', entity.end,'; label=',entity.label, 'kb_id=',entity.kb_id)
    print("A", entity._,type(entity._))
    print("B", entity._.kb_ents,type(entity._.kb_ents))
    print("C", entity._.kb_ents[0],type(entity._.kb_ents[0]))
    print("D", entity._.kb_ents[0][0],type(entity._.kb_ents[0][0]))
    print("E", linker.kb.cui_to_entity[entity._.kb_ents[0][0]], type(linker.kb.cui_to_entity[entity._.kb_ents[0][0]]))


# Each entity is linked to UMLS with a score
# (currently just char-3gram matching).
#for umls_ent in entity._.kb_ents:
#    print(linker.kb.cui_to_entity[umls_ent[0]])
