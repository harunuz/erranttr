**[EN]**[[TR]](README_tr.md)

# ERRANT-TR
The official implementation of [Towards Automatic Grammatical Error Type Classification for Turkish](https://aclanthology.org/2023.eacl-srw.14/)

The Turkish version of [ERRANT](https://www.aclweb.org/anthology/P17-1074/), an automatic evaluation toolkit for grammatical error correction tasks.

This code builds upon ERRANT's [official repo](https://github.com/chrisjbryant/errant). The underlying logic is the same, so please refer to ERRANT about
taxonomy and usage.

### Dependencies
- [zemberek-python](https://github.com/loodos/zemberek-python)
- [rapidfuzz](https://github.com/maxbachmann/RapidFuzz)

Before running the code (specifically classifier.py), you need to download and extract following files
from the assets of 0.1.0 release:
1. **tr_TR.aff** (taken from [hunspell-tr](https://github.com/tdd-ai/hunspell-tr))
2. **TS_Corpus_Turkish_Word_List.zip** (taken from a great data source [tdd](https://data.tdd.ai/#/16e5fbcf-a658-424d-b50c-4454a4b367dc))

## Data

The dataset consists of 106 correct-erroneous sentence pairs obtained from various academic resources. The samples were 
labeled by a linguist with a broader error categories. In order to use the error categories in ERRANT one needs to map 
some labels to their correspondents. See Section 4.1 of the paper for detailed information about dataset.

The sentence pairs, labeled data in M2 format, labeled data with mapped labels in M2 format and the predictions of ERRANT-TR
can be found in [erranttr/tr/resources](erranttr/tr/resources) folder.

### Note on Reproducibility
We discovered a minor bug concerning some error types (specifically NOUN:POSS and SPELL) after the paper submission. 
There are minor changes in the code. This version works as intended. Please use this version. We provide the
output of the first version (the one that went with the paper submission) in
[predictions_W_MAPPED_LABELS_IN_PAPER.txt](erranttr/tr/resources/predictions_W_MAPPED_LABELS_IN_PAPER.txt) file in
resources directory.

### Error Type Mapping
ERRANT-TR works on a broader error types than ERRANT. In order to compare the works
in a meaningful way, we map these new types to the closest types in ERRANT. The error type matching table
and simple examples are given below.

| New Label           | ERRANT Correspondent | Example                                  |
|---------------------|----------------------|------------------------------------------|
| DA                  | SPELL                | cay ictim -> çay içtim                   |
| ACCENT              | SPELL                | geliyom -> geliyorum                     |
| NOUN:CASE           | NOUN:INFL            | evde gidiyorum -> eve gidiyorum          |
| NOUN:NUM:SURF       | NOUN:INFL            | saatlar -> saatler                       |
| ADJ:CASE            | ADJ                  | korkaklar sevmem -> korkakları sevmem    |
| VERB:INFL:TENSE     | VERB:TENSE           | dün geliyorum -> dün gelmiştim           |
| NOUN:PHRASE         | OTHER                | kitabının kapağı -> kitabın kapağı       |
| NOUN:STC:NEG        | VERB                 | bende kalem değil -> bende kalem yok     |
| NOUN-VERB:INFL:CASE | NOUN:INFL            | gelme düşünüyorum -> gelmeyi düşünüyorum |
| PRON:CASE           | NOUN:INFL            | o söyledim -> ona söyledim               |
| PRON:INFL           | NOUN:INFL            | odan aldım -> ondan aldım                |
| PRON:POSS           | NOUN:POSS            | onu kalemi -> onun kalemi                |

### Usage
Go to erranttr package directory (erranttr/erranttr)
```
cd /path/to/erranttr/erranttr
```

Run process.py file to process parallel data and write in M2 file format. It
reads [sentences.txt](erranttr/tr/resources/sentences.txt) file and takes the output file name as input. 

```
python process.py predictions.txt`
```
Run map_labels.py in order to map some ERRANT-TR specific error types to their ERRANT correspondents.
```
python map_labels.py predictions.txt
```
Run compare_m2.py to compare ground truth and the predictions in M2 formats.

```
python commands/compare_m2.py -hyp "output/predictions_W_MAPPED_LABELS.txt" -ref tr/resources/eval_data_W_MAPPED_LABELS.txt -b 0.5 -cse -cat 2
```



