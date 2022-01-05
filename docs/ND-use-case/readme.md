
# Use-case: preparing the ND datasets for LBD contrast analysis

* Top: [Main Documentation](..)
* Previous: [tdc-tools: UMLS and MeSH utilities](../umls-mesh-utilities)
* Next: [Convert the Medline MeSH descriptors by PMID to DCM format](../mesh-descriptors-by-pmid)

## Overview

This document examplifies the process of preparing two datasets (KD-based and PTC-based) for LBD analysis based on concepts co-occurrences using `tdc-tools`.

## Requirements

Both the KD and PTC datasets must have been [obtained](../input-data-format) and [converted to the document-concept format](../generating-doc-concept-matrix-data).

## List of target concepts

In this use case we are interested in all the concepts related to Neurodegenerative Diseases (NDs). We use the [UMLS and MeSH utlilities](../umls-mesh-utilities) in order to collect these concepts, both as MeSH (for PTC) and CUI (for KD):

```
echo  D019636 | collect-mesh-hierarchy.py -x desc2021.xml ND.mesh
cut -f 1 ND.mesh | sed 's/^/MESH:/g' >ND.mesh.targets
```

```
echo C0524851 | collect-umls-hierarchy.py /tmp/umls/ ND.cui
cut -f 1 ND.cui >ND.cui.targets
```


## Collect individual and joint frequency by concept

See [Collecting individual and joint frequency by concept](../collecting-frequency-by-concept) for more details.

### Individual frequency

This step is done for all the concepts in the data, it does not depend on the target concepts.

```
get-frequency-from-doc-concept-matrix-all-variants.sh  PTC.dcm/ PTC.concept-freq
```

```
get-frequency-from-doc-concept-matrix-all-variants.sh  KD.dcm/ KD.concept-freq
```

### Joint frequency

```
get-frequency-from-doc-concept-matrix-all-variants.sh -p -j PTC.dcm/ PTC.joint ND.mesh.targets
```

Duration: around 6 hours (single process).

```
get-frequency-from-doc-concept-matrix-all-variants.sh -j KD.dcm/ KD.joint ND.cui.targets
```

Duration: around 20 hours (single process).

Check that there was no error and delete the error files:

```
cat *.joint/*/*/*err
rm -f *.joint/*/*/*err
```

## Aggregating frequencies across years

### PTC

```
mkdir PTC.tmp
for level in by-doc by-sent; do for view in unfiltered-medline pmc-articles abstracts+articles; do sum-freq-over-years.py /tmp/ptc.concept-freq/$level/$view/ 0 3000 PTC.tmp/$level.$view.indiv.aggregated0; done; done
```

```
for level in by-doc by-sent; do for view in unfiltered-medline pmc-articles abstracts+articles; do sum-freq-over-years.py -j PTC.joint/$level/$view/ 0 3000 PTC.tmp/$level.$view.joint.aggregated0; done; done
```

In PTC the semantic groups/categories require an additional step:

```
for f in PTC.tmp/*indiv.aggregated0; do ptc-aggregate-across-types.py -t  $f ${f%%0}; done
for f in PTC.tmp/*joint.aggregated0; do ptc-aggregate-across-types.py -j  $f ${f%%0}; done
```

### KD

```
mkdir KD.tmp
for level in by-doc by-sent; do for view in unfiltered-medline pmc-articles abstracts+articles; do sum-freq-over-years.py /tmp/kd.concept-freq/$level/$view/ 0 3000 KD.tmp/$level.$view.indiv.aggregated; done; done
```

```
for level in by-doc by-sent; do for view in unfiltered-medline pmc-articles abstracts+articles; do sum-freq-over-years.py -j KD.joint/$level/$view/ 0 3000 KD.tmp/$level.$view.joint.aggregated; done; done
```

## Add term and group for every concept

This step requires the UMLS data, see [UMLS and MeSH utlilities](../umls-mesh-utilities).

### PTC


```
ls PTC.tmp/*indiv.aggregated | add-term-from-umls.py -G /tmp/umls/ .with-term
```


### KD

```
ls KD.tmp/*indiv.aggregated | add-term-from-umls.py -g SemGroups.txt /tmp/umls/ .with-term
```

## Classify by target

Every output file is named using the target concept id and contains a list of related concepts. It follows the following format: 

```
<concept id> <indiv freq> <term> <list of groups> <joint freq>
```

Note: `<list of groups>` is a (possibly empty) list of groups separated by spaces.

### PTC

```
for level in by-doc by-sent; do for view in unfiltered-medline pmc-articles abstracts+articles; do cat ND.mesh.targets | sed 's/^MESH://g'  | classify-coocurrences-by-target.py -p PTC.tmp/$level.$view.indiv.aggregated.with-term PTC.tmp/$level.$view.joint.aggregated results/PTC/$level/$view; done; done
```

### KD

```
for level in by-doc by-sent; do for view in unfiltered-medline pmc-articles abstracts+articles; do cat ND.cui.t
argets | classify-coocurrences-by-target.py KD.tmp/$level.$view.indiv.aggregated.with-term KD.tmp/$level.$view.joint.aggregated results/KD/$level/$view; done; done
```

## Copy the totals files

### PTC

```
for level in by-doc by-sent; do for view in unfiltered-medline pmc-articles abstracts+articles; do cp PTC.tmp/$level.$view.indiv.aggregated0.total results/PTC/$level/$view/total.tsv; done; done
```

### KD

```
for level in by-doc by-sent; do for view in unfiltered-medline pmc-articles abstracts+articles; do cp KD.tmp/$level.$view.indiv.aggregated.total results/KD/$level/$view/total.tsv; done; done
```


The final datasets are in the directory `results` which is organized as follows: 

* The directory structure is `<dataset_id>/<level>/<view>`, where `dataset_id` is either KD or PTC.
* Each `view` directory contains:
   * a file `targets.tsv` with columns `<target id> <indiv frequency> <term> <list of groups>` 
   * a file `<target_id>` for every target concept present in th data, with columns `<concept id> <indiv freq> <term> <list of groups> <joint freq>`
   * a file `total.tsv` with a single line: `<total nb documents> <total nb concepts>`
  
  
## Generate the 'tidy' version for every output file

A reformated version of every output file is generated where the 4th column `<list of groups>` (see above) is split so that every row contains exactly one group. 

* If there are multiple groups the other columns are duplicated
* If there is no group the empty group column is replaced with `NA` 

```
ls results/*/*/*/* | grep -v '.tsv' | while read f; do list-column-to-tidy-format.py -c 4 $f $f.key-id-group; done
```
