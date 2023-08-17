import os
import sys

# append project root (/path/to/erranttr
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import erranttr


def main(args):
    print("Loading resources...")
    # Load Errant
    annotator = erranttr.load("tr")

    print("Processing parallel files...")
    fname = args.fname if os.path.splitext(args.fname)[1] == '.txt' else f"{args.fname}.txt"

    with open(r'tr/resources/sentences.txt', 'r', encoding='utf-8') as fi, \
            open(f"output/{fname}", "w", encoding='utf-8') as out_m2:

        # Process each line of all input files
        i = 0
        for line in fi:

            # Get the original and all the corrected texts
            origt, cor = line.strip().split('\t')
            # Skip the line if orig is empty
            if not origt:
                continue
            i += 1
            # DEBUG
            # print(f"{i} - {origt}")
            orig = annotator.parse(origt)
            # Write orig to the output m2 file
            out_m2.write(" ".join(["S"] + [token.word_analysis.inp for token in orig]) + "\n")
            # Loop through the corrected texts
            cors = [cor]
            for cor_id, cor in enumerate(cors):
                cor = cor.strip()
                # If the texts are the same, write a noop edit
                if origt.strip() == cor:
                    out_m2.write(noop_edit(cor_id) + "\n")
                # Otherwise, do extra processing
                else:
                    # Parse cor with spacy
                    cor = annotator.parse(cor)
                    # Align the texts and extract and classify the edits
                    edits = annotator.annotate(orig, cor)
                    # Loop through the edits
                    for edit in edits:
                        # Write the edit to the output m2 file
                        out_m2.write(edit.to_m2(cor_id) + "\n")
            # Write a newline when we have processed all corrections for each line
            out_m2.write("\n")


# Input: A coder id
# Output: A noop edit; i.e. text contains no edits
def noop_edit(id=0):
    return "A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||" + str(id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("fname", type=str)
    _args = parser.parse_args()

    os.makedirs('output', exist_ok=True)

    main(_args)
