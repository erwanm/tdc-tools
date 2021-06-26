# tdc-tools documentation

This is the documentation of the [TDC Tools repository](https://github.com/erwanm/tdc-tools). TDC stands for Tabular Document-Concept.

## Contents

* [TDC: input data format](input-data-format)
* [Converting PTC data to TDC format](converting-ptc-data-to-tdc-format)
* [Generate the doc-concept matrix](#generating-doc-concept-matrix-data)
* [Collect individual and joint frequency by concept](collecting-frequency-by-concept)
* [tdc-tools: UMLS and MeSH utilities](umls-mesh-utilities)
* [Use-case: preparing the ND dataset for LBD contrast analysis](ND-use-case)


## Overview

This repository contains Python and Bash scripts to generate and manipulate data in the Tabular Document-Concept (TDC) format. TDC is a format specificailly designed to represent the biomedical literature as a collection of documents represented by their concepts. In particular it facilitates the extraction of a knowledge graph of concepts and can be used as a support for Literature-Based Discovery (LBD).

Most of the biomedical literature is available for download from [Medline](https://www.nlm.nih.gov/medline/index.html) and [PubMedCentral](https://www.ncbi.nlm.nih.gov/pmc/) (PMC). [PubTatorCentral](https://www.ncbi.nlm.nih.gov/research/pubtator) (PTC) offers an alternative to the raw data format with the BioC format. While the PTC data is much richer and BioC more convenient than the raw xml format, these formats are all fairly low level: very detailed, quite complex to parse, and not very convenient to capture high-level relations between articles or concepts. By contrast the TDC format is a high-level representation of the literature where each document is considered as a collection of concepts and the documents are grouped by year of publication. The format is meant to facilitate the extraction of the concepts individual and joint frequency.

* Common format for different extraction methods, e.g. using the [Knowledge Discovery (KD)](https://github.com/erwanm/kd-data-tools) system or PTC.
* Suited for Literature-Based Discovery and similar applications
* Tabular format akin to a relational database 
* Year-based format to facilitate analysis across time or filtering by range of years
* Preserves link of a concept with its source sentence/document (this is possible but not implemented) 
* Additional utilities based on UMLS/MeSH resources

### Software requirements

Most scripts require only Python 3 and a few standard Python libraries. 

* [Converting PTC data to TDC format](converting-ptc-data-to-tdc-format) requires the following additional libraries: `bioc`, `spacy`, `scispacy`.
* Using the KD data (see [TDC: input data format](input-data-format)) requires additional software.

### Data requirements

The scripts can be used with any dataset in the TDC format. See [TDC: input data format](input-data-format).

### Setup

In this documentation we assume that the scripts are available in the `$PATH` environment variable. For this setup run the following command from the `tdc-tools` directory:

```
export PATH=$PATH:$(pwd)/code
```

Note that the scripts can also be called with their path, e.g. `code/build-doc-concept-matrix-all-variants.sh`.

