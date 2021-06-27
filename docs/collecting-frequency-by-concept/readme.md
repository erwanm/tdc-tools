# Collecting individual and joint frequency by concept

* Top: [Main documentation](..)
* Previous: [Generate the doc-concept matrix](../generating-doc-concept-matrix-data)
* Next: [tdc-tools: UMLS and MeSH utilities](../umls-mesh-utilities)

# I. Individual frequency by concept

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
get-frequency-from-doc-concept-matrix-all-variants.sh  PTC.dcm/ PTC.concept-freq
```

* Estimated duration: 2.5 hours
* Size: less than 1 GB

### KD data

```
get-frequency-from-doc-concept-matrix-all-variants.sh  KD.dcm/ KD.concept-freq
```

* Estimated duration: 5 hours
* Size: less than 1 GB

## Collecting data stats (optional)

For a single data dir:

```
collect-data-stats.sh PTC.concept-freq/ >17-PTC-2021/data-stats.tsv
```

```
../tdc-tools/code/collect-data-stats.sh KD.concept-freq >16-KD-2021/data-stats.tsv
```

For several data dirs:

```
collect-data-stats.sh PTC.concept-freq/ KD.concept-freq >18-contrast-method-experiments/global-stats.tsv
```

# II. Joint frequency by pairs of concepts

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
get-frequency-from-doc-concept-matrix-all-variants.sh -p -j PTC.dcm/ PTC.joint-targets PTC.targets

real    365m33.960s
user    359m29.992s
sys     1m18.763s
```

* Duration: around 6 hours

### KD

Printing the tasks for parallel execution:

```
rm -f KD.joint-targets
get-frequency-from-doc-concept-matrix-all-variants.sh -w -j KD.dcm/ KD.joint-targets KD.targets >tasks
mkdir jobs
split -a 4 -d -l 1 tasks jobs/job.
for f in jobs/job.*; do echo -e '#!/bin/bash\n#SBATCH -p compute\n' > $f.sh; cat "$f" >> "$f.sh"; done
for f in jobs/*.sh; do sbatch $f; done
```

* Duration on the cluster: one or two hours (longest jobs)
* This produces `.err` files for each task which should be empty and can be deleted afterwards.
