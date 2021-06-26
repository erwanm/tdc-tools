# Converting PTC data to TDC format

* Top: [Main documentation](..)
* Previous: [TDC: input data format](../input-data-format)
* Next: [Generate the doc-concept matrix](../generating-doc-concept-matrix-data)

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
PTC-to-TDC.py <PTC input dir> <output dir>
```

This command reads the full PTC data, processes every document and writes the corresponding data in the output TDC format. 

* It is useful to test the system on a subset of files
* It would certainly take a very long time, hence the second way below.

### Multiple processes by range of years

Currently the only way to decompose the task into parallel batches is to process a range of years:

```
PTC-to-TDC.py <PTC input dir> <output dir> <start year> <end year>
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

See also [Details about the TDC output format for PTC and differences with KD output](../input-data-format/#details-about-the-tdc-output-format-for-ptc-and-differences-with-kd-output)


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
create-symlinks-data-views.sh PTC.TDC
```

### Compressing

```
mksquashfs PTC2021-TDC PTC2021-TDC.sqsh -comp xz
```
