"""
modified from https://github.com/chrisjbryant/errant/blob/master/errant/en/merger.py
"""

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from erranttr.alignment import Alignment
    from zemberek.morphology.analysis.sentence_word_analysis import SentenceWordAnalysis
from itertools import combinations, groupby
from re import sub
from string import punctuation
from rapidfuzz.distance import Indel

from zemberek.core.turkish import PrimaryPos as PPOS
from erranttr.edit import Edit
import erranttr.text_utils as tu

# Merger resources
open_pos = {PPOS.Adjective, PPOS.Adverb, PPOS.Noun, PPOS.Verb}


# Input: An Alignment object
# Output: A list of Edit objects
def get_rule_edits(alignment: 'Alignment') -> List[Edit]:
    edits = []
    # Split alignment into groups of M, T and rest. (T has a number after it)
    for op, group in groupby(alignment.align_seq,
                             lambda x: x[0][0] if x[0][0] in {"M", "T"} else False):
        group = list(group)
        # Ignore M
        if op == "M":
            continue
        # T is always split
        elif op == "T":
            for seq in group:
                edits.append(Edit(alignment.orig, alignment.cor, seq[1:]))
        # Process D, I and S subsequence
        else:
            processed = process_seq(group, alignment)
            # Turn the processed sequence into edits
            for seq in processed:
                edits.append(Edit(alignment.orig, alignment.cor, seq[1:]))
    return edits


# Input 1: A sequence of adjacent D, I and/or S alignments
# Input 2: An Alignment object
# Output: A sequence of merged/split alignments
def process_seq(seq, alignment: 'Alignment'):
    # Return single alignments
    if len(seq) <= 1:
        return seq
    # Get the ops for the whole sequence
    ops = [op[0] for op in seq]
    # Merge all D xor I ops. (95% of human multi-token edits contain S).
    if set(ops) == {"D"} or set(ops) == {"I"}:
        return merge_edits(seq)

    content = False  # True if edit includes a content word
    # Get indices of all start-end combinations in the seq: 012 = 01, 02, 12
    combos = list(combinations(range(0, len(seq)), 2))
    # Sort them starting with largest spans first
    combos.sort(key=lambda x: x[1] - x[0], reverse=True)
    # Loop through combos
    for start, end in combos:
        # Ignore ranges that do NOT contain a substitution.
        if "S" not in ops[start:end + 1]:
            continue
        # Get the tokens in orig and cor. They will now never be empty.
        o = alignment.orig[seq[start][1]:seq[end][2]]
        c = alignment.cor[seq[start][3]:seq[end][4]]
        # Case changes
        if tu.lower(o[-1].word_analysis.inp) == tu.lower(c[-1].word_analysis.inp):
            # Merge first token I or D: [Cat -> The big cat]
            if start == 0 and ((len(o) == 1 and c[0].word_analysis.inp[0].isupper()) or
                               (len(c) == 1 and o[0].word_analysis.inp[0].isupper())):
                return merge_edits(seq[start:end + 1]) + \
                       process_seq(seq[end + 1:], alignment)
            # Merge with previous punctuation: [, we -> . We], [we -> . We]
            if (len(o) > 1 and is_punct(o[-2])) or \
                    (len(c) > 1 and is_punct(c[-2])):
                return process_seq(seq[:end - 1], alignment) + \
                       merge_edits(seq[end - 1:end + 1]) + \
                       process_seq(seq[end + 1:], alignment)
        # Merge whitespace/hyphens: [acat -> a cat], [sub - way -> subway]
        s_str = sub("['-]", "", "".join([tu.lower(tok.word_analysis.inp) for tok in o]))
        t_str = sub("['-]", "", "".join([tu.lower(tok.word_analysis.inp) for tok in c]))
        if s_str == t_str:
            return process_seq(seq[:start], alignment) + \
                   merge_edits(seq[start:end + 1]) + \
                   process_seq(seq[end + 1:], alignment)

        pos_set = set([tok.best_analysis.item.primary_pos for tok in o] +
                      [tok.best_analysis.item.primary_pos for tok in c])
        if len(o) != len(c) and (len(pos_set) == 1 or
                                 pos_set.issubset({PPOS.Verb})):
            return process_seq(seq[:start], alignment) + \
                   merge_edits(seq[start:end + 1]) + \
                   process_seq(seq[end + 1:], alignment)
        # Split rules take effect when we get to the smallest chunks
        if end - start < 2:
            # Split adjacent substitutions
            if len(o) == len(c) == 2:
                return process_seq(seq[:start + 1], alignment) + \
                       process_seq(seq[start + 1:], alignment)
            # Split similar substitutions at sequence boundaries
            if (ops[start] == "S" and char_cost(o[0], c[0]) > 0.75) or \
                    (ops[end] == "S" and char_cost(o[-1], c[-1]) > 0.75):
                return process_seq(seq[:start + 1], alignment) + \
                       process_seq(seq[start + 1:], alignment)
        # Set content word flag
        if not pos_set.isdisjoint(open_pos):
            content = True
    # Merge sequences that contain content words
    if content:
        return merge_edits(seq)
    else:
        return seq


# Check whether token is punctuation
def is_punct(token: 'SentenceWordAnalysis'):
    return token.best_analysis.item.primary_pos == PPOS.Punctuation or token.word_analysis.inp in punctuation


# Calculate the cost of character alignment; i.e. char similarity
def char_cost(a: 'SentenceWordAnalysis', b: 'SentenceWordAnalysis'):
    return 1 - Indel.normalized_distance(a.word_analysis.inp, b.word_analysis.inp)


# Merge the input alignment sequence to a single edit span
def merge_edits(seq):
    if seq:
        return [("X", seq[0][1], seq[-1][2], seq[0][3], seq[-1][4])]
    else:
        return seq
