"""
modified from https://github.com/chrisjbryant/errant/blob/master/errant/annotator.py
"""

from zemberek import TurkishMorphology, TurkishTokenizer
from zemberek.core.turkish import TurkishAlphabet
from zemberek.morphology.lexicon import RootLexicon

from erranttr.alignment import Alignment

# Main ERRANT Annotator class
class Annotator:

    TR_ALPH = TurkishAlphabet.INSTANCE

    # Input 1: A string language id: e.g. "en"
    # Input 2: A spacy processing object for the language
    # Input 3: A merging module for the language
    # Input 4: A classifier module for the language
    def __init__(self, lang, merger=None, classifier=None):
        self.lang = lang
        self.zemberek = TurkishMorphology.builder(RootLexicon.get_default()).use_informal_analysis().build()
        self.tokenizer = TurkishTokenizer.DEFAULT
        self.merger = merger
        self.classifier = classifier

    # Input 1: A text string
    # Input 2: A flag for word tokenization
    # Output: The input string parsed by spacy
    def parse(self, text, tokenize=False):
        if tokenize:
            out = self.tokenizer.tokenize(text)
            return out
        out = self.zemberek.analyze_and_disambiguate(text)
        return out

    # Input 1: An original text string parsed by spacy
    # Input 2: A corrected text string parsed by spacy
    # Input 3: A flag for standard Levenshtein alignment
    # Output: An Alignment object
    def align(self, orig, cor, lev=False):
        return Alignment(orig, cor, lev)

    # Input 1: An Alignment object
    # Input 2: A flag for merging strategy
    # Output: A list of Edit objects
    def merge(self, alignment, merging="rules"):
        # rules: Rule-based merging
        if merging == "rules":
            edits = self.merger.get_rule_edits(alignment)
        # all-split: Don't merge anything
        elif merging == "all-split":
            edits = alignment.get_all_split_edits()
        # all-merge: Merge all adjacent non-match ops
        elif merging == "all-merge":
            edits = alignment.get_all_merge_edits()
        # all-equal: Merge all edits of the same operation type
        elif merging == "all-equal":
            edits = alignment.get_all_equal_edits()
        # Unknown
        else:
            raise Exception("Unknown merging strategy. Choose from: "
                "rules, all-split, all-merge, all-equal.")
        return edits

    # Input: An Edit object
    # Output: The same Edit object with an updated error type
    def classify(self, edit):
        return self.classifier.classify(edit)

    # Input 1: An original text string parsed by spacy
    # Input 2: A corrected text string parsed by spacy
    # Input 3: A flag for standard Levenshtein alignment
    # Input 4: A flag for merging strategy
    # Output: A list of automatically extracted, typed Edit objects
    def annotate(self, orig, cor, lev=False, merging="rules"):
        alignment = self.align(orig, cor, lev)
        edits = self.merge(alignment, merging)
        for edit in edits:
            edit = self.classify(edit)
        return edits

