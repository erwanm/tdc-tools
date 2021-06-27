
# Use-case: preparing the ND datasets for LBD contrast analysis

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

See [Collecting individual and joint frequency by concept](../collecting-frequency-by-concept) for detailed instructions.

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

