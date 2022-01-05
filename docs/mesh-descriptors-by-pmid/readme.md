
# Convert the Medline MeSH descriptors by PMID to DCM (Doc-Concept Matrix) format

* Top: [Main Documentation](..)
* Previous: [Use-case: preparing the ND dataset for LBD contrast analysis](../ND-use-case)

## Overview

Instructions for converting the list of Medline MeSH descriptors by PMID to the DCM format, usable by other parts of `tdc-tools`.

## Requirements

The input data is the list of MeSH descriptors by PMID. 

1. The file `mesh-descriptors-by-pmid.tsv` can be obtained with the [KD fork](https://github.com/erwanm/knowledgediscovery#medline-mesh-descriptors-by-pmid), as [described in the documentation here](https://github.com/erwanm/knowledgediscovery#extracting-mesh-descriptors-by-pmid-from-medline).
2. The duplicates should be removed using the [KD Tools repository](https://github.com/erwanm/kd-data-tools). This process [is described here](https://github.com/erwanm/kd-data-tools#step-2-remove-duplicate-abstracts) and summarized below:

```
extract-non-latest-pmid-versions.pl mesh-descriptors-by-pmid.tsv non-latest-pmid-versions.tsv
echo mesh-descriptors-by-pmid.tsv | ../kd-data-tools/bin/discard-non-latest-pmid-versions.pl -c 3 non-latest-pmid-versions.tsv output
mv output/mesh-descriptors-by-pmid.tsv mesh-descriptors-by-pmid.deduplicated.tsv
```


### Format of the file `mesh-descriptors-by-pmid.deduplicated.tsv`

(copied from [here](https://github.com/erwanm/knowledgediscovery#format-of-the-output-files))

```
<pmid> <year> <pmid version> <journal> <title> <mesh list>
```

Where `<mesh list>` is a comma-separated list of Mesh descriptors together with the value for 'MajorTopicYN' after each of them (separated by `|`). Example:

```
D005845|N,D006268|Y,D006273|Y,D006739|Y,D006786|N,D014481|N
```


## Generating the DCM format

```
mkdir medline-mesh-decriptors
build-dcm-from-mesh-descriptors-by-pmid.py mesh-descriptors-by-pmid.deduplicated.tsv medline-mesh-decriptors/dcm
```

## Temporary fix for the KD bug "season instead of year"

To this date there is [a bug](https://github.com/erwanm/knowledgediscovery/issues/4) in the [KD fork](https://github.com/erwanm/knowledgediscovery#medline-mesh-descriptors-by-pmid) leading to some entries having an invalid year.

In case this bug hasn't been fixed by then, this will remove the erroneous entries from the data:

```
cd medline-mesh-decriptors/dcm
rm -f Autu fall Fall spri Spri summ Summ Wint
cd ../..
```

## Collecting the individual and joint frequency by concept

Same process as described [here](../collecting-frequency-by-concept):

```
mkdir medline-mesh-descriptors/concept-freq
mkdir medline-mesh-descriptors/joint-freq
cd medline-mesh-descriptors/
for f in dcm/*; do echo $f; ls $f | get-frequency-from-doc-concept-matrix.py concept-freq/$(basename $f); done
for f in dcm/*; do echo $f; ls $f | get-frequency-from-doc-concept-matrix.py -j joint-freq/$(basename $f); done
```


