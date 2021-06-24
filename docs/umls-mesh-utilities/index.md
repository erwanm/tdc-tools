# tdc-tools: UMLS and MeSH utilities

[Main Documentation](..)

tdc-tools contains several python script to read and manipulate the [UMLS](https://www.nlm.nih.gov/research/umls/index.html) data and the [MeSH](https://www.nlm.nih.gov/mesh/meshhome.html) hierarchy.

- Extract all the concepts in a subtree of the UMLS or MeSH hierarchy, i.e. find all the concepts more specific than the input concept.
- Map a concept id to its term (text description) and/or semantic group (UMLS)
- Convert from MeSH descriptor to UMLS CUI and conversely

## Requirements

* The UMLS metathesaurus must be downloaded manually from https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html
   * Select "UMLS Metathesaurus Files" (no need for the "full release")
   * Access requires a free UTC account.
* The MeSH tree structure is contained in the file `desc20xx.xml` which can be dowloaded from https://www.nlm.nih.gov/databases/download/mesh.html
   * Select "Current Production Year" in XML format
   * Download `desc20xx.xml`

## `collect-umls-hierarchy.py`: extract all the concepts more specific than the input concepts

Reads a list of CUI concepts (one by line) from STDIN and extracts from the UMLS data all their 'descendants' according to the UMLS hierarchy.

```

```

## `add-term-from-umls.py`: map a concept id to its term and semantic group

Reads a list of input tsv files with a concept id column (either a UMLS CUI id or a MeSH descriptor) from STDIN and maps the id to a term using the UMLS data. For each input file `f` an output file `f.suffix` is created with an additional term column. 

```
```
