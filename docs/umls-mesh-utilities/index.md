# tdc-tools: UMLS and MeSH utilities

* Top: [Main Documentation](..)
* Previous: [Collect individual and joint frequency by concept](../collecting-frequency-by-concept)
* Next: [Use-case: preparing the ND dataset for LBD contrast analysis](../ND-use-case)

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

## Extract all the concepts more specific than the input CUI

Reads a list of CUI concepts (one by line) from STDIN and extracts from the UMLS data all their 'descendants' according to the UMLS hierarchy.

In this example we use the CUI [C0524851](https://uts.nlm.nih.gov/uts/umls/concept/C0524851) (Neurodegenerative Disorders) as the root of the subtree. The [UMLS browser](https://uts.nlm.nih.gov/uts/umls/home) can be used to find the concept id for a term. In this command we assume that the UMLS data is available in the `umls` directory (which must contain the subdirectory `META`).


```
echo C0524851 | collect-umls-hierarchy.py /tmp/umls/ ND0.cui
```

Note: the output contains all the descendant concepts as first column, and for each concept the second column contains a space-separated list containing the different ways this node was reached. Each element in the list is a triple `<depth>,<parent CUI>,<relation>`. In the default setting `<relation>` is always `RN` (Relation Narrower), but this can be extended with options `-i` or `-I`.


## Extract all the concepts more specific than the input MeSH descriptor

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



## Map a concept id to its corresponding term and semantic group

Reads a list of input tsv files with a concept id column (either a UMLS CUI id or a MeSH descriptor) from STDIN and maps the id to a term using the UMLS data. For each input file `f` an output file `f.suffix` is created with an additional term column. 

The UMLS "semantic group" associated to a CUI can also be added by using option `-g <UMLS sem groups file>`, where the file can be downloaded from https://lhncbc.nlm.nih.gov/semanticnetwork/download/SemGroups.txt.

```
ls ND0.cui | add-term-from-umls.py -g SemGroups.txt /tmp/umls/ .details
```

The script can also read MeSH descriptors as input with option `-m`:

```
ls ND0.mesh | add-term-from-umls.py -m -g SemGroups.txt /tmp/umls/ .details
```

Note: The input files are read from STDIN, this way it is possible to process a batch of input files while loading the UMLS data in memory only once.

## Convert between UMLS CUIs and MeSH descriptors

Converts a column of CUIs to MeSH or conversely.
In general an input concept id may have any number of output ids (possibly zero). As a result the new column contains (in general) a list of ids which can be empty.

```
ls ND0.cui | convert-umls-to-mesh.py /tmp/umls/ .to-mesh
```

```
ls ND0.mesh | convert-umls-to-mesh.py -r /tmp/umls/ .to-cui
```
## Reformat a list column ("tidy" format)

Some of the scripts above generate an output with a column containing a (possibly empty) list of elements (for example list of semantic groups). Depending on the application it can be convenient to reformat this kind of data so that each row contain a single value in this column.

```
> head -n 3 ND0.mesh.to-cui
D019636 Neurodegenerative Diseases      C10.574 C0270715 C0524851 C0751733
D000070627      Chronic Traumatic Encephalopathy        C10.574.250     C0750973 C0750972 C4082769 C1527318
D000080874      Synucleinopathies       C10.574.928     C5191670
```


```
list-column-to-tidy-format.py ND0.mesh.to-cui ND0.mesh.to-cui.one-cui-by-line
```

```
 head ND0.mesh.to-cui.one-cui-by-line 
D019636 Neurodegenerative Diseases      C10.574 C0270715
D019636 Neurodegenerative Diseases      C10.574 C0524851
D019636 Neurodegenerative Diseases      C10.574 C0751733
D000070627      Chronic Traumatic Encephalopathy        C10.574.250     C0750973
D000070627      Chronic Traumatic Encephalopathy        C10.574.250     C0750972
D000070627      Chronic Traumatic Encephalopathy        C10.574.250     C4082769
D000070627      Chronic Traumatic Encephalopathy        C10.574.250     C1527318
D000080874      Synucleinopathies       C10.574.928     C5191670
D016262 Postpoliomyelitis Syndrome      C10.574.827     C0080040
D016472 Motor Neuron Disease    C10.574.562     C0543858
```


## Observations about UMLS and MeSH identifiers

The two systems differ in many ways, please refer to their documentation for details. As of 2021:

* MeSH includes around 30,000 unique concepts.
* UMLS includes around 4.4 millions unique concepts.

Naturally this implies that there is no one-to-one correspondence between the two systems, so conversions are imperfect. For example the UMLS CUIs obtained from converting a group of MeSH descriptors do not cover all the CUIs found from UMLS:

```
> wc -l ND0.cui
311 ND0.cui
> cut -f 4 ND0.mesh.to-cui | tr ' ' '\n' | sort -u | wc -l
210
```

In the other direction, the MeSH descriptors obtained from converting a group of CUIs includes more identifiers than the ones generated drectly from MeSH:

```
> wc -l ND0.mesh
76 ND0.mesh
> cut -f 3 ND0.cui.to-mesh | tr ' ' '\n' | sort -u | wc -l
97
```

Note that this may also depend on the relations between concepts in the two systems and the options used when extracting the hierarchy.

