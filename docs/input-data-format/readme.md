# TDC: input data format

* Top [Main documentation](..)
* Next [Converting PTC data to TDC format](converting-ptc-data-to-tdc-format)


## Overview

TDC (Tabular Document-Concept)  is a format specificailly designed to represent the biomedical literature as a collection of documents represented by their concepts. In particular it facilitates the extraction of a knowledge graph of concepts and can be used as a support for Literature-Based Discovery (LBD).

The format is meant as a form of standard which disconnects the stage of data extraction from the the stage of high level exploitation:

* Upstream, different datasets and extraction methods can be represented as TDC.
* Downtream, different applications and methods (e.g. LBD methods) can exploit any dataset represented as TDC.

Currently two main options are proposed to obtain a TDC representation of the biomedical literature:

- [PubTatorCentral](https://www.ncbi.nlm.nih.gov/research/pubtator/) conveniently provides Medline/PMC data after annotation and disambiguation.
    - [Downloading and preparing the raw PTC data](#collecting-pubtator-central-PTC-data) 
    - [Converting the PTC data to TDC format](../converting-ptc-data-to-tdc-format)
- The raw Medline/PMC data can be converted to TDC and disambiguated using the following tools:
    - [This fork of the Knowedge Discovery (KD) repository](https://github.com/erwanm/knowledgediscovery) (The [original code](https://github.com/jakelever/knowledgediscovery) was made by Jake Lever)
    - The in-house disambiguation code ["KD Data Tools"](https://github.com/erwanm/kd-data-tools)
  

## The TDC format

* Note: description from [this KnowledgeDiscovery fork](https://github.com/erwanm/knowledgediscovery). The format was originally designed for the KD data, hence the use UMLS CUIs as concept identifiers (CUIs can be replaced with any concept id).

For each input document, three output files are generated: `.raw`, `.tok`, `.cuis`. The format of these files is described below.

### `.raw` file

Abstracts:

```
<pmid> <year> <title> <abstract content>
```

Full article:

```
<pmid> <year> <title+subtitle> <abstract content> <paper content>
```

Where `<paper content>` includes the xml elements `article`, `back` and `floating`.

### `.tok` file

Full content of the sentences with ids

```
<pmid> <year> <partId> <elemId> <sentNo> <sentence words>
```

### `.cuis` file

Extracted CUIs by position, i.e. for every position and length where at least one CUI is found the list of candidate CUIs (synonyms).

The CUIs are provided as integer ids, as used internally by the original KD system.

```
<pmid> <partId> <elemId> <sentNo> <cuis list> <position> <length>
```




## Collecting PubTator Central (PTC) data

The [PubTator Central (PTC)](https://www.ncbi.nlm.nih.gov/research/pubtator/) data can be downloaded in bulk in the BioC format as follows:

```
wget ftp://ftp.ncbi.nlm.nih.gov/pub/lu/PubTatorCentral/PubTatorCentral_BioCXML/*
```

Estimated duration: 12 hours.

Despite the `.gz` extension the files are simple `tar` archives. To extract them:

```
for f in BioCXML.*gz; do tar xf $f; done
```

* ''Caution:'' the uncompressed data requires 438G (January 2021 version).

To save space the resulting directory can be compressed:

```
mksquashfs BioCXML/ BioCXML.sqsh -comp xz
```

* Estimated duration: 30 hours.
* The compressed size is 69G.

## Details about the TDC output format for PTC and differences with KD output

* In the TDC fomat the `.tok` file is meant to primarily represent sentence-level tokenization. Word-level tokenization is optional.
    * In the KD output in TDC format, word-level tokenization is also provided and the position of a concept is represented as a a token index
    * By contrast the PTC output doesn't provide word-level tokenization and represents the position as a char offset.
         * This is due to the fact that the PTC BioC format doesn't provide word-level tokenization, and applying SciSpacy tokenization turned out not to be compatible with the PTC annotations.
* The format of the concept column is also different between KD and PTC output:
    * In KD an occurrence can match multiple UMLS concepts, so the concept column is made of a comma-separated list of concepts.
        * Incidentally this is why the KD output requires a disambiguation step.
    * In PTC the concepts are already disambiguated and it's very rare that multiple concepts are provided for the same occurrence. Therefore the concept column represents a single concept. The rare cases of multiple concepts are stored on different lines.
    * In PTC the concept column is made of an identifier and a type separated by `@`: `id@type`
    * In PTC a concept identifier can contain pretty much any character, including the comma `,` and even the separator `@` (at least one case).
        * **Important:** when parsing the concept string `id@type` only the last `@` should be interpreted as separator in the string (the `type` cannot contain the separator but the `id` can).

