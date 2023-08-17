import os
import sys
import argparse

# append project root (/path/to/erranttr
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

mapped_labels = {
    "DA": "SPELL",
    "ACCENT": "SPELL",
    "NOUN:CASE": "NOUN:INFL",
    "NOUN:NUM:SURF": "NOUN:INFL",
    # "VERB:INFL:KIP_CEKIMLERI": "VERB:INFL",
    "ADJ:CASE": "ADJ",
    "VERB:INFL:TENSE": "VERB:TENSE",
    "NOUN:PHRASE": "OTHER",
    "NOUN:STC:NEG": "VERB",
    "NOUN-VERB:INFL:CASE": "NOUN:INFL",
    "PRON:CASE": "NOUN:INFL",
    "PRON:INFL": "NOUN:INFL",
    "PRON:POSS": "NOUN:POSS"
}


def main(args):
    fname = args.fname if os.path.splitext(args.fname)[1] == '.txt' else f"{args.fname}.txt"
    inf = f"output/{fname}"

    os.makedirs('output', exist_ok=True)
    outf = f"output/{os.path.splitext(fname)[0]}_W_MAPPED_LABELS.txt"

    with open(inf, 'r', encoding='utf-8') as fi, open(outf, 'w', encoding='utf-8') as fo:
        text = fi.read()

        for k, v in mapped_labels.items():
            text = text.replace(k, v)
        fo.write(text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("fname", type=str)
    _args = parser.parse_args()

    main(_args)
