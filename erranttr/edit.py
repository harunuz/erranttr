"""
modified from https://github.com/chrisjbryant/errant/blob/master/errant/edit.py
"""

from typing import TYPE_CHECKING, Sequence, Union

if TYPE_CHECKING:
    from zemberek.morphology.analysis.sentence_word_analysis import SentenceWordAnalysis
    from zemberek.morphology.analysis.sentence_analysis import SentenceAnalysis

# ERRANT edit class
class Edit:

    # Input 1: An original text string parsed by zemberek
    # Input 2: A corrected text string parsed by zemberek
    # Input 3: A token span edit list: [o_start, o_end, c_start, c_end]
    # Input 4: An error type string, if known
    def __init__(
            self,
            orig: Union[Sequence['SentenceWordAnalysis'], 'SentenceAnalysis'],
            cor: Union[Sequence['SentenceWordAnalysis'], 'SentenceAnalysis'],
            edit,
            type="NA"
    ):
        # Orig offsets, spacy tokens and string
        self.o_start = edit[0]
        self.o_end = edit[1]
        self.o_toks = orig[self.o_start:self.o_end]
        self.o_str = ' '.join([t.word_analysis.inp for t in self.o_toks]) if self.o_toks else ""
        # Cor offsets, spacy tokens and string
        self.c_start = edit[2]
        self.c_end = edit[3]
        self.c_toks = cor[self.c_start:self.c_end]
        self.c_str = ' '.join([t.word_analysis.inp for t in self.c_toks]) if self.c_toks else ""
        # Error type
        self.type = type

        self.orig_best_analyses = [a.best_analysis for a in self.o_toks] if self.o_toks else []
        self.cor_best_analyses = [a.best_analysis for a in self.c_toks] if self.c_toks else []

    # Input: An id for the annotator
    # Output: An edit string formatted for an M2 file
    def to_m2(self, id=0):
        span = " ".join(["A", str(self.o_start), str(self.o_end)])
        cor_toks_str = " ".join([tok.word_analysis.inp for tok in self.c_toks])
        return "|||".join([span, self.type, cor_toks_str, "REQUIRED", "-NONE-", str(id)])

    # Edit object string representation
    def __str__(self):
        orig = "Orig: "+str([self.o_start, self.o_end, self.o_str])
        cor = "Cor: "+str([self.c_start, self.c_end, self.c_str])
        type = "Type: "+repr(self.type)
        return ", ".join([orig, cor, type])