
# Generating the doc-concept matrix data

* Top: [Main documentation](..)
* Previous: [Converting PTC data to TDC format](../converting-ptc-data-to-tdc-format)
* Next: [Collect individual and joint frequency by concept](../collecting-frequency-by-concept)


## Introduction

* The document-concept matrix format represents every instance with the set of concepts contained in this instance.
* The segmentation in instances can be made at the level of a document (abstract or article) or of a sentence (or both).
* The script creates exactly one output file for one input file. The format is:

```
<year> <doc id> <list of doc-concepts>
```

where `<list of doc-concepts>` contains a space separated list of `<concept id>:<freq>`. 

* **Important:** the separator `:` can appear in `<concept id>` but not in `<freq>`, therefore the last item `freq` should be extracted first when parsing this string.

## Usage 

* A script is provided which runs the whole process sequentially for all 6 variants of the data (by sentence/document x 3 directories), see below.
* If needed it's straightforward to process the files by batch since there's a 1:1 correspondence between input and output file.
* The script can be used in the same way with either the PTC data (in TDC format) or the KD data (in TDC format).

### PTC data

```
build-doc-concept-matrix-all-variants.sh <PTC TDC input dir> PTC.dcm
```

* Estimated duration: 1h30
* Size: 31 GB


### KD data

* Note: the script expects the directory structure as described in the [KD-data-tools](https://github.com/erwanm/kd-data-tools) documentation.
* Don't forget the `-k` option (multiple concepts, for non-disambiguated concepts left)

```
build-doc-concept-matrix-all-variants.sh -k <KD TDC input dir> KD.dcm
```

* Estimated duration: 5 hours
* Size: 52 GB

### Compressing (optional)

```
mksquashfs PTC.dcm PTC.dcm.sqsh
```

```
mksquashfs KD.dcm KD.dcm.sqsh
```
