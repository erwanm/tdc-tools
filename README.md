# tdc-tools
Tools for manipulating Tabular Document-Concept format

# Overview

This repository contains Python and Bash scripts to generate and manipulate data in the Tabular Document-Concept (TDC) format. TDC is a format specificailly designed to represent the biomedical literature as a collection of documents represented by their concepts. In particular it facilitates the extraction of a knowledge graph of concepts and can be used as a support for Literature-Based Discovery (LBD).

Most of the biomedical literature is available for download from [Medline](https://www.nlm.nih.gov/medline/index.html) and [PubMedCentral](https://www.ncbi.nlm.nih.gov/pmc/) (PMC). [PubTatorCentral](https://www.ncbi.nlm.nih.gov/research/pubtator) (PTC) offers an alternative to the raw data format with the BioC format. While the PTC data is much richer and BioC more convenient than the raw xml format, these formats are all fairly low level: very detailed, quite complex to parse, and not very convenient to capture high-level relations between articles or concepts. By contrast the TDC format is a high-level representation of the literature where each document is considered as a collection of concepts and the documents are grouped by year of publication. The format is meant to facilitate the extraction of the concepts individual and joint frequency.

* Common format for different extraction methods, e.g. using the [Knowledge Discovery (KD)](https://github.com/erwanm/kd-data-tools) system or PTC.
* Suited for Literature-Based Discovery and similar applications
* Tabular format akin to a relational database 
* Year-based format to facilitate analysis across time or filtering by range of years
* Preserves link of a concept with its source sentence/document (this is possible but not implemented) 
* Main scripts:
    * [Parse PTC to TDC](#ii-converting-ptc-data-to-tdc-format)
    * [Generate the doc-concept matrix](#iii-generating-doc-concept-matrix-data)
    * [Collect individual frequency by concept](#iv-collecting-individual-frequency-by-concept)
    * [Collect joint frequency by concept](#v-collecting-joint-frequency-by-pairs-of-concepts)
  


# I. Collecting PubTator Central (PTC) data


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

# II. Converting PTC data to TDC format

## Output structure

The output data is stored n the TDC format in three subdirectories:


* `filtered-medline`: Medline documents (abstracts) which are not present in PMC.
* `pmc-abstracts`: Abstracts obtained from PMC. These abstracts are also contained in `pmc-articles`. 
* `pmc-articles`: Full articles from PMC.

The output is structured this way in order to:

* Allow the retrieval of different "views" of the data:
    * `unfiltered-medline`: all the Medline abstracts = `filtered-medline` + `pmc-abstracts`
    * `pmc-articles`: all the PMC full articles
    * `abstracts+articles`: the whole Medline+PMC data without duplicate abstracts = `filtered-medline` + `pmc-articles`
* Minimize the processing computations by avoiding processing all the "views" independently (since they overlap).

Inside every subdirectory the files are organized by year (first part of the filename). There is a maximum number of documents by file in order to facilitate batch processing so there can be several files for every year. There is a special case for when the year of the document is undefined (treated as year `0000`, see below).

**Important:** the process requires a lot of computing time (a few months if using a single process) and **the resulting data is 317 GB** (for the January 2021 PTC data).

## Requirements


The conversion script `PTC-to-TDC.py` requires the following Python modules: `bioc`, `spacy`, `scispacy`.

### Optional: udocker environment

In a non-root environment a udocker container can be created as follows:

```
udocker create --name=bioc ubuntu
udocker run -v ~ pybioc
apt update
apt upgrade
apt install python python3-pip
pip3 install bioc spacy scispacy
```


## Usage

The script `PTC-to-TDC.py` can be used in two ways described below.

### Single full process

```
python3 tdc-tools/code/PTC-to-TDC.py <PTC input dir> <output dir>
```

This command reads the full PTC data, processes every document and writes the corresponding data in the output TDC format. 

* It is useful to test the system on a subset of files
* It would certainly take a very long time, hence the second way below.

### Multiple processes by range of years

Currently the only way to decompose the task into parallel batches is to process a range of years:

```
python3 tdc-tools/code/PTC-to-TDC.py <PTC input dir> <output dir> <start year> <end year>
```

* `<end year>` is excluded, so that for example start=1960, end=1965 means years 1960, 1961, 1962, 1963, 1965 (5 years).
* The script reads the whole data but processes only the documents in the specified range of years. This means that the recent years which have much more documents take much more time.

The script `generate-PTC-to-TDC-jobs-by-year.sh` can be used to generate slurm jobs by year as follows:

```
rm -rf ptc-jobs; mkdir ptc-jobs; tdc-tools/code/generate-PTC-to-TDC-jobs-by-year.sh data/PubTatorCentral.sqsh 1950 ptc-jobs/job PTC.TDC compute
for f in ptc-jobs/*sh; do sbatch $f; done
```

Note that some jobs (recent years) will require around 10 days of computation.

### Handling of errors/oddities in the PTC data

* Some Medline documents are provided without the year of publication for some reason: around 46,000 out of 28 millions. These are assigned year `0000` and then processed/stored normally.
    * **Important:** any subsequent process based on publication years should avoid the documents with year `0000`. These are provided for the sake of completeness when processing the whole data independently of publication year.
    * Note: while the PTC idiosyncrasies have been studied carefully, it is possible that this is the result of some kind of bug.
* The PTC documents are annotated with concepts but sometimes the concept string is empty or contains only an hyphen `-` (130m cases out of 865m). These cases are discarded.
* A few other less common technical issues in the data are reported in the output of the script. 

### Details about the TDC output format for PTC and differences with KD output

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

## Wrapping up (optional)

### Global log summary across batches

If the script was run independently by range of years the outputs by year can be aggregated as follows:

```
ls *out | grep -v slurm | while read f; do grep "Info:" "$f"; done | cut -f 1 -d '='  | sort -u | while read line; do echo -n "$line = ";  ls *out | grep -v slurm | while read f; do grep "$line =" "$f"; done | cut -d '=' -f 2 | awk '{s+=$1} END {print s}'; done
```

### Archiving the logs

```
mkdir PTC.TDC/PTC-to-TDC.logs
rm -f slurm*out
ls *err *out
mv *err *out  PTC.TDC/PTC-to-TDC.logs
```

### Creating symlinks for `unfiltered-medline` and `abstracts+articles` views (optional)

```
tdc-tools/code/create-symlinks-data-views.sh PTC.TDC
```

### Compressing

```
mksquashfs PTC2021-TDC PTC2021-TDC.sqsh -comp xz
```



# III. Generating doc-concept matrix data

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
tdc-tools/code/build-doc-concept-matrix-all-variants.sh <PTC TDC input dir> PTC.dcm
```

* Estimated duration: 1h30
* Size: 31 GB


### KD data

* Note: the script expects the directory structure as described in the KD-data-tools documentation.
* Don't forget the `-k` option (multiple concepts, for non-disambiguated concepts left)

```
tdc-tools/code/build-doc-concept-matrix-all-variants.sh -k <KD TDC input dir> KD.dcm
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

# IV. Collecting individual frequency by concept

## Introduction

* For every year, collect the individual frequency for every concept from the doc-concept matrix files.
* A single file is created for every year and every "data view":
    * The multiple batch files from the document-concept matrix format are aggregated by year
    * The doc-concept matrix batch files can be aggregated from several directories: typically for the PTC data: 
         * the directories `filtered-medline` and `pmc-abstracts` are combined into data view `unfiltered-medline`
         * the directories `filtered-medline` and `pmc-articles` are combined into data view `abstracts+articles`

## Format

### "Data views" (directory structure)

General: structure `<level>/<view>/` where:

* `level` is:
    * `by-doc`
    * `by-sent`
* `view` is:
    * `abstracts+articles `
    * `pmc-articles`
    * `unfiltered-medline`

In every `<level>/<view>/` directory, for every year there are two files:

### File `<year>`

```
<year> <concept id> <doc frequency> <total frequency>
```

where:

* `<doc frequency>` is the number of documents containing the concept (max = total number of documents)
** in other words, interpret each document as a ''set'' of concepts.
* `<total frequency>` is the cumulated frequency, i.e. number of occurrences (max = total number of concepts across all documents)

Note: the number of lines is the number of unique concepts present in the year.


###  File `<year>.total`

```
<year> <nb unique concepts> <nb docs> <nb concepts occurrences>
```


## Usage

* The individual script (producing one file as output) is `get-frequency-from-doc-concept-matrix.py`, it reads multiple input files provided on STDIN.
* Note: optionally a list of target concepts can be provided. In this case only the target frequency are written in the detailed output, but the `.total` files still count all the concepts (thus the true probability can still be calculated).
* For convenience a bash script runs the whole process:

### PTC data

```
tdc-tools/code/get-frequency-from-doc-concept-matrix-all-variants.sh  PTC.dcm/ PTC.concept-freq
```

* Estimated duration: 2.5 hours
* Size: less than 1 GB

### KD data

```
tdc-tools/code/get-frequency-from-doc-concept-matrix-all-variants.sh  KD.dcm/ KD.concept-freq
```

* Estimated duration: 5 hours
* Size: less than 1 GB

## Collecting data stats (optional)

For a single data dir:

```
../tdc-tools/code/collect-data-stats.sh PTC.concept-freq/ >17-PTC-2021/data-stats.tsv
```

```
../tdc-tools/code/collect-data-stats.sh KD.concept-freq >16-KD-2021/data-stats.tsv
```

For several data dirs:

```
../tdc-tools/code/collect-data-stats.sh PTC.concept-freq/ KD.concept-freq >18-contrast-method-experiments/global-stats.tsv
```

# V. Collecting joint frequency by pairs of concepts

* Goal: count cooccurrences for pairs of concepts A B.
* It is highly recommended to provide a list of target concepts in order to avoid the massive number of pairs resulting from the cartesian product of all the concepts.


## Format

The output follows exactly the same directory structure as the individual frequency output (see above).

## File `year`

```
<year> <concept1> <concept2> <joint freq>
```


where `joint freq` is the number of documents containing the pair of concepts.

## Usage

* Performed by the same script `get-frequency-from-doc-concept-matrix.py`, see above.
* For convenience a bash script runs the whole process. This script can either run the indivudual tasks for every year/variant or print the tasks to STDOUT for distributed execution.

In the examples below a list of 10 target concepts is used.

### PTC 

Running all the tasks at once:

```
../tdc-tools/code/get-frequency-from-doc-concept-matrix-all-variants.sh -p -j PTC.dcm/ PTC.joint-targets 18-contrast-method-experiments/PTC.targets

real    365m33.960s
user    359m29.992s
sys     1m18.763s
```

* Duration: around 6 hours

### KD

Printing the tasks for parallel execution:

```
rm -f KD.joint-targets
./tdc-tools/code/get-frequency-from-doc-concept-matrix-all-variants.sh -w -j KD.dcm/ KD.joint-targets 18-contrast-method-experiments/KD.targets >tasks
mkdir jobs
split -a 4 -d -l 1 tasks jobs/job.
for f in jobs/job.*; do echo -e '#!/bin/bash\n#SBATCH -p compute\n' > $f.sh; cat "$f" >> "$f.sh"; done
for f in jobs/*.sh; do sbatch $f; done
```

* Duration on the cluster: one or two hours (longest jobs)
* This produces `.err` files for each task which should be empty and can be deleted afterwards.
