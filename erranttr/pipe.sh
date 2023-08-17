#!/bin/bash
source ../venv/bin/activate

f="predictions";

python process.py $f

python map_labels.py $f

python commands/compare_m2.py -hyp "output/"$f"_W_MAPPED_LABELS.txt" -ref tr/resources/eval_data_W_MAPPED_LABELS.txt -b 0.5 -cse -cat 2