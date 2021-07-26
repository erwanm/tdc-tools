# tdc-tools
Tools for representing and manipulating data in the Tabular Document-Concept (TDC) format

* Documentation: https://erwanm.github.io/tdc-tools/
* Associated paper: **pending** (if you use this code for your research please cite the paper).
* KD and PTC datasets generated from the January 2021 data: https://zenodo.org/record/5138386


### Overview

This repository contains Python and Bash scripts to generate and manipulate data in the Tabular Document-Concept (TDC) format. TDC is a format specificailly designed to represent the biomedical literature as a collection of documents represented by their concepts. In particular it facilitates the extraction of a knowledge graph of concepts and can be used as a support for Literature-Based Discovery (LBD).

Most of the biomedical literature is available for download from [Medline](https://www.nlm.nih.gov/medline/index.html) and [PubMedCentral](https://www.ncbi.nlm.nih.gov/pmc/) (PMC). [PubTatorCentral](https://www.ncbi.nlm.nih.gov/research/pubtator) (PTC) offers an alternative to the raw data format with the BioC format. While the PTC data is much richer and BioC more convenient than the raw xml format, these formats are all fairly low level: very detailed, quite complex to parse, and not very convenient to capture high-level relations between articles or concepts. By contrast the TDC format is a high-level representation of the literature where each document is considered as a collection of concepts and the documents are grouped by year of publication. The format is meant to facilitate the extraction of the concepts individual and joint frequency.

* Common format for different extraction methods, e.g. using the [Knowledge Discovery (KD)](https://github.com/erwanm/kd-data-tools) system or PTC.
* Suited for Literature-Based Discovery and similar applications
* Tabular format akin to a relational database 
* Year-based format to facilitate analysis across time or filtering by range of years
* Preserves link of a concept with its source sentence/document (this is possible but not implemented) 

