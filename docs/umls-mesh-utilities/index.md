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

## `collect-umls-hierarchy.py`: extract all the concepts more specific than the input CUI

Reads a list of CUI concepts (one by line) from STDIN and extracts from the UMLS data all their 'descendants' according to the UMLS hierarchy.

In this example we use the CUI [C0524851](https://uts.nlm.nih.gov/uts/umls/concept/C0524851) (Neurodegenerative Disorders) as the root of the subtree. The [UMLS browser](https://uts.nlm.nih.gov/uts/umls/home) can be used to find the concept id for a term. In this command we assume that the UMLS data is available in the `umls` directory (which must contain the subdirectory `META`).


```
echo C0524851 | collect-umls-hierarchy.py /tmp/umls/ ND0.cui
```

Note: the output contains all the descendant concepts as first column, and for each concept the second column contains a space-separated list containing the different ways this node was reached. Each element in the list is a triple `<depth>,<parent CUI>,<relation>`. In the default setting `<relation>` is always `RN` (Relation Narrower), but this can be extended with options `-i` or `-I`.


## `collect-mesh-hierarchy.py`: extract all the concepts more specific than the input MeSH descriptor

This script is similar to `collect-umls-hierarchy.py` but uses MeSH descriptors instead of UMLS CUIs and reads the MeSH data. It reads a list of MeSH concepts (one by line) from STDIN and extracts all their 'descendants' according to the MeSH hierarchy.

In the following examples we use the MeSH descriptor D019636 corresponding to the term "Neurodegenerative Diseases" (one can use the [MeSH browser](https://meshb.nlm.nih.gov/search) to identify concepts ids). Note that it is also possible to provide input concepts as MeSH tree ids (e.g. C10.574 instead of D019636) with option `-i`. 

There are two ways to use this script. By default the script reads a simplified representation of the MeSH hierarchy which is obtained with the script `parse-mesh-desc-xml.py`:

```
parse-mesh-desc-xml.py desc2021.xml mesh.tsv
echo  D019636 | collect-mesh-hierarchy.py mesh.tsv ND0.mesh
```

The original MeSH file can also be provided directly to the script with the option `-x`:

```
echo  D019636 | collect-mesh-hierarchy.py -x desc2021.xml ND0.mesh
```

The first variant is faster because it does not parse the original xml file every time `collect-mesh-hierarchy.py` is called.



## `add-term-from-umls.py`: map a concept id to its corresponding term and semantic group

Reads a list of input tsv files with a concept id column (either a UMLS CUI id or a MeSH descriptor) from STDIN and maps the id to a term using the UMLS data. For each input file `f` an output file `f.suffix` is created with an additional term column. 

The UMLS "semantic group" associated to a CUI can also be added by using option `-g <UMLS sem groups file>`, where the file can be downloaded from https://lhncbc.nlm.nih.gov/semanticnetwork/download/SemGroups.txt.

```
ls ND0.cui | add-term-from-umls.py -g SemGroups.txt /tmp/umls/ .details
```

The script can also read MeSH descriptors as input with option `-m`:

```
ls ND0.mesh | add-term-from-umls.py -m -g SemGroups.txt /tmp/umls/ .details
```

## `convert-umls-to-mesh.py`: convert between UMLS CUIs and MeSH descriptors

Converts a column of CUIs to MeSH or conversely.
In general an input concept id may have any number of output ids (possibly zero). As a result the new column contains (in general) a list of ids which can be empty.

```
ls ND0.cui | convert-umls-to-mesh.py /tmp/umls/ .to-mesh
```

```
 ls ND0.mesh | convert-umls-to-mesh.py /tmp/umls/ .to-cui
```
## `list-column-to-tidy-format.py`: reformat a list column

