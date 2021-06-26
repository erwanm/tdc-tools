# TDC: input data format


## Format

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

