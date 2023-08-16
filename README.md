**[EN]**[[TR]](README_tr.md)

# ERRANT-TR
The official implementation of [Towards Automatic Grammatical Error Type Classification for Turkish](https://aclanthology.org/2023.eacl-srw.14/)

The Turkish version of [ERRANT](https://www.aclweb.org/anthology/P17-1074/), an automatic evaluation toolkit for grammatical error correction tasks.

This code builds upon ERRANT's [official repo](https://github.com/chrisjbryant/errant). The underlying logic is the same, so please refer to ERRANT about
taxonomy and usage.

### Dependencies
- [zemberek-python](https://github.com/loodos/zemberek-python)
- [rapidfuzz](https://github.com/maxbachmann/RapidFuzz)


## Data

The dataset consists of 106 correct-erroneous sentence pairs obtained from various academic resources. The samples were 
labeled by a linguist with a broader error categories. In order to use the error categories in ERRANT one needs to map 
some labels to their correspondents. See Section 4.1 of the paper for detailed information about dataset.

The sentence pairs, labeled data in M2 format, labeled data with mapped labels in M2 format and the predictions of ERRANT-TR
can be found in [erranttr/tr/resources](erranttr/tr/resources) folder.

### Usage

Run process.py file to process parallel data and write in M2 file format. It
reads [sentences.txt](erranttr/tr/resources/sentences.txt) file and takes the output file name as input. 

`python erranttr/erranttr/process.py predictions.txt`

Run map_labels.py in order to map some ERRANT-TR specific error types to their ERRANT correspondents.

`python erranttr/erranttr/map_labels.py predictions.txt`

Run compare_m2.py to compare ground truth and the predictions in M2 formats.

```
python erranttr/erranttr/commands/compare_m2.py -hyp erranttr/erranttr/tr/resources/eval_data_preds_W_MAPPED_LABELS_0.txt -ref erranttr/erranttr/tr/resources/eval_data_W_MAPPED_LABELS_0.txt -b 0.5 -cse -cat 2
```

### Note

Before running the code (specifically classifier.py), you need to download and extract following files
from the assets of 0.1.0 release:
1. **tr_TR.aff**
2. **TS_Corpus_Turkish_Word_List.zip**


### Not
Kullanmadan önce [erranttr/tr/resources](erranttr/tr/resources) dizinine,
sağda 0.1.0 versiyonunun eklerinde bulunan **tr_TR.aff** ve 
**TS_Corpus_Turkish_Word_List.zip** dosyalarını indirip zip olanları 
çıkarmanız gerekmektedir. 