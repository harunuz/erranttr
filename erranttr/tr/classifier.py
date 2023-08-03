from pathlib import Path
from typing import Sequence, TYPE_CHECKING, Set

if TYPE_CHECKING:
    from zemberek.morphology.analysis.sentence_word_analysis import SentenceWordAnalysis
    from zemberek.morphology.analysis.single_analysis import SingleAnalysis

from rapidfuzz.distance import Levenshtein
from zemberek.core.turkish import PrimaryPos as PPOS, SecondaryPos as SPOS
from zemberek.morphology.morphotactics.turkish_morphotactics import get_morpheme_map

from erranttr.edit import Edit
import erranttr.text_utils as tu


# Load Hunspell word list
# def load_word_list(path):
#    with open(path) as word_list:
#        return set([word.strip() for word in word_list])

def load_word_list(path):
    with open(path, 'r', encoding='utf-8') as fi:
        words = [l.split('/')[0].strip() for l in fi]

    return set(words[1:])  # first line is the number of words in the dictionary


def load_suffix_list(path):
    with open(path, 'r', encoding='utf-8') as fi:
        words = [l for l in fi if '.' in l]

    return set([w.split()[-2] for w in words])


# Classifier resources
base_dir = Path(__file__).resolve().parent

num_set = {PPOS.Numeral}
verb_set = {PPOS.Verb}

open_pos1 = {PPOS.Adjective, PPOS.Adverb, PPOS.Noun, PPOS.Verb}


morpheme_map = get_morpheme_map()
general_pos_set = {PPOS.Adjective, PPOS.Adverb, PPOS.Determiner, PPOS.Punctuation}

plural_morphemes = {'P2pl', 'A2pl', 'P3pl', 'P1pl', 'A3pl', 'A1pl'}

kisi_ekleri = {'A2pl', 'A3pl', 'A1pl', 'A2sg', 'A3sg', 'A1sg'}

possessives = {'P2pl', 'P3pl', 'P1pl', 'P2sg', 'P3sg', 'P1sg'}

case_suffixes = {"Nom", "Dat", "Acc", "Abl", "Loc", "Ins", "Gen", "Equ"}

tenses = {"Pres", "Past", "Narr", "Cond", "Prog1", "Prog2", "Aor", "Fut"}

spell = load_word_list(base_dir / "resources" / 'TS_Corpus_Turkish_Word_List.txt')
suffix = load_suffix_list(base_dir / "resources" / 'tr_TR.aff')


# Input: An Edit object
# Output: The same Edit object with an updated error type
def classify(edit: Edit):
    # Nothing to nothing is a detected but not corrected edit
    if not edit.o_toks and not edit.c_toks:
        edit.type = "UNK"
    # Missing
    elif not edit.o_toks and edit.c_toks:
        op = "M:"
        cat = get_one_sided_type(edit.c_toks)
        edit.type = op + cat
    # Unnecessary
    elif edit.o_toks and not edit.c_toks:
        op = "U:"
        cat = get_one_sided_type(edit.o_toks)
        edit.type = op + cat
    # Replacement and special cases
    else:
        # Same to same is a detected but not corrected edit
        if edit.o_str == edit.c_str:
            edit.type = "UNK"
        # Special: Ignore case change at the end of multi token edits
        # E.g. [Doctor -> The doctor], [, since -> . Since]
        # Classify the edit as if the last token wasn't there
        elif tu.lower(edit.o_toks[-1].word_analysis.inp) == tu.lower(edit.c_toks[-1].word_analysis.inp) and \
                (len(edit.o_toks) > 1 or len(edit.c_toks) > 1):
            # Store a copy of the full orig and cor toks
            all_o_toks = edit.o_toks[:]
            all_c_toks = edit.c_toks[:]
            # Truncate the instance toks for classification
            edit.o_toks = edit.o_toks[:-1]
            edit.c_toks = edit.c_toks[:-1]
            # Classify the truncated edit
            edit = classify(edit)
            # Restore the full orig and cor toks
            edit.o_toks = all_o_toks
            edit.c_toks = all_c_toks
        # Replacement
        else:
            op = "R:"
            cat = get_two_sided_type(edit.c_toks, edit.o_toks)  # TODO CHANGE THE PARAMETER NAMES IN THE FUNCTION
            edit.type = op + cat
    return edit


# Input: Spacy tokens
# Output: An error type string based on input tokens from orig or cor
# When one side of the edit is null, we can only use the other side
def get_one_sided_type(toks: Sequence['SentenceWordAnalysis']):
    # Special cases
    if len(toks) == 1:
        # Determiner's bir, bu, şu
        if toks[0].best_analysis.item.primary_pos == PPOS.Determiner:
            return PPOS.Determiner.short_form.upper()

    pos_list = [t.best_analysis.item.primary_pos for t in toks]
    pos_set = set(pos_list)

    if pos_set == num_set:
        return PPOS.Numeral.short_form.upper()

    if pos_set == verb_set:
        return PPOS.Verb.short_form.upper()

    if len(pos_set) == 1 and pos_set.issubset(general_pos_set):
        return pos_list[0].short_form.upper()
    # Tricky cases
    else:
        return "OTHER"


# Input 1: Spacy orig tokens
# Input 2: Spacy cor tokens
# Output: An error type string based on orig AND cor
def get_two_sided_type(o_toks: Sequence['SentenceWordAnalysis'], c_toks: Sequence['SentenceWordAnalysis']):
    # Extract pos tags and parse info from the toks as lists

    # Orthography; i.e. whitespace and/or case errors.
    if only_orth_change(o_toks, c_toks):
        return "ORTH"
    # Word Order; only matches exact reordering.
    if exact_reordering(o_toks, c_toks):
        return "WO"
    # BURADAYIZ
    # 1:1 replacements (very common)
    if len(o_toks) == len(c_toks) == 1:
        o_str = o_toks[0].word_analysis.inp
        c_str = c_toks[0].word_analysis.inp
        o_lower = tu.lower(o_str)
        c_lower = tu.lower(c_str)
        # 1. SPECIAL CASES
        # ASCIIFICATION
        if diacritization_error(o_str, c_str):
            return "DA"

        # ***** MISSING *****
        # ACCENT -> added to the verb section
        # SOCIAL
        # ***** MISSING *****

        # WARNING
        # THIS PART REQUIRES A KNOWN ANALYSIS FOR BOTH TOKENS, WE MAY REVISIT THIS PART IN ORDER TO EITHER
        # ELIMINATE THIS REQUIREMENT OR PROVIDE A BETTER SOLUTION WHILE DOING THE ANALYSIS
        if not c_toks[0].best_analysis.item.is_unknown():  # and not c_toks[0].best_analysis.item.is_unknown()

            o_last_group = o_toks[0].best_analysis.get_group(
                len(o_toks[0].best_analysis.group_boundaries) - 1
            )
            c_last_group = c_toks[0].best_analysis.get_group(
                len(c_toks[0].best_analysis.group_boundaries) - 1
            )

            o_last_group_morphemes = [m.morpheme for m in o_last_group.morphemes]
            c_last_group_morphemes = [m.morpheme for m in c_last_group.morphemes]

            # possible POS tags =>
            # ['Noun', 'Adj', 'Verb', 'Pron', 'Adv', 'Conj', 'Punc', 'Ques', 'Postp', 'Det', 'Num', 'Dup', 'Interj']
            o_pos = next((m.pos for m in o_last_group_morphemes if m.pos is not None), None)
            c_pos = next((m.pos for m in c_last_group_morphemes if m.pos is not None), None)

            o_root_pos = o_toks[0].best_analysis.item.primary_pos
            c_root_pos = c_toks[0].best_analysis.item.primary_pos

            # NOUN:NUM:SURF tekil-cogul hatalari
            c_is_plural = next((True for m in c_last_group_morphemes if m.id_ in plural_morphemes), False)
            o_lemma = o_toks[0].best_analysis.item.lemma
            c_lemma = c_toks[0].best_analysis.item.lemma

            # NOUN:NUM
            # çoğul-tekil hatası
            if c_pos == PPOS.Noun and noun_num_error(o_toks[0], c_toks[0]):
                return "NOUN:NUM"

            # NOUN:STC:NEG
            if (tu.lower(o_toks[0].best_analysis.item.lemma) == 'yok' and
                tu.lower(c_toks[0].best_analysis.item.lemma) == 'değil') or (
                    tu.lower(o_toks[0].best_analysis.item.lemma) == 'değil' and
                    tu.lower(c_toks[0].best_analysis.item.lemma) == 'yok'):
                return "NOUN:STC:NEG"

            # VERB:SVA
            if verb_sva_error(o_toks[0], c_toks[0]):
                return "VERB:SVA"

            if c_is_plural:
                if (c_lemma in o_toks[0].word_analysis.inp) or (c_lemma in o_toks[0].best_analysis.item.lemma):
                    if 'ler' in o_lower or 'lar' in o_lower:
                        return "NOUN:NUM:SURF"

            # isim, zarf, sifat
            if c_pos in {PPOS.Noun, PPOS.Adverb, PPOS.Adjective, PPOS.Pronoun}:

                if o_toks[0].best_analysis.item.is_unknown():

                    str_sim = Levenshtein.normalized_similarity(o_lower, c_lower)
                    if 0 <= len(o_lower) <= 5 and str_sim >= 0.8:
                        return "SPELL"
                    elif str_sim >= 0.6:
                        return "SPELL"
                    return "OTHER"

                # eger sozlukteki kelime girdileri ve kelime kokleri ayni degilse
                if o_toks[0].best_analysis.item != c_toks[0].best_analysis.item and \
                        o_toks[0].best_analysis.item.root != c_toks[0].best_analysis.item.root:

                    if c_pos in {PPOS.Adjective, PPOS.Adverb, PPOS.Pronoun}:
                        return c_pos.short_form.upper()

                    # NOUN
                    tag_ = "NOUN"
                    if o_lower.startswith(c_toks[0].best_analysis.get_stem()) or \
                            o_lower.startswith(c_toks[0].best_analysis.item.root):

                        o_case_suffixes = {m for m in o_last_group_morphemes if m.id_ in case_suffixes}
                        c_case_suffixes = {m for m in c_last_group_morphemes if m.id_ in case_suffixes}

                        # check if this is enough, we might need MorphemeData (Morpheme with surface form)
                        if o_case_suffixes != c_case_suffixes:
                            return tag_ + ":CASE"

                        o_case_possessives = {m for m in o_last_group_morphemes if m.id_ in possessives}
                        c_case_possessives = {m for m in c_last_group_morphemes if m.id_ in possessives}

                        # iyelik ekleri ortusmuyor
                        if o_case_possessives != c_case_possessives:
                            return tag_ + ":POSS"


                        return tag_ + ":INFL"

                    return tag_

                    # if stems are equal
                if tu.lower(o_toks[0].best_analysis.item.root) == tu.lower(c_toks[0].best_analysis.item.root):

                    tag_ = c_pos.short_form.upper()

                    if c_root_pos == PPOS.Verb:
                        # isim-fiil, zarf-fiil, sifat-fiil
                        tag_ += '-VERB:INFL'

                    o_case_suffixes = {m for m in o_last_group_morphemes if m.id_ in case_suffixes}
                    c_case_suffixes = {m for m in c_last_group_morphemes if m.id_ in case_suffixes}

                    # check if this is enough, we might need MorphemeData (Morpheme with surface form)
                    if o_case_suffixes != c_case_suffixes:
                        return tag_ + ":CASE"

                    o_case_possessives = {m for m in o_last_group_morphemes if m.id_ in possessives}
                    c_case_possessives = {m for m in c_last_group_morphemes if m.id_ in possessives}

                    # iyelik ekleri ortusmuyor
                    if o_case_possessives != c_case_possessives:
                        return tag_ + ":POSS"

            if c_pos == PPOS.Verb:
                # eger kelime fiilse

                # eger sozlukteki kelime girdileri ve kelime kokleri ayni degilse
                if o_toks[0].best_analysis.item != c_toks[0].best_analysis.item:
                    if not o_toks[0].best_analysis.is_unknown():
                        return "VERB"

                    # o is unknown
                    stem = c_toks[0].best_analysis.get_stem()
                    if o_lower.startswith(stem) or o_lower.startswith(c_toks[0].best_analysis.item.root):
                        str_sim = Levenshtein.normalized_similarity(
                            c_toks[0].best_analysis.get_ending(),
                            o_lower[len(stem):]
                        )
                        if str_sim >= 0.85:
                            return "SPELL"
                        return "VERB:INFL"

                    str_sim = Levenshtein.normalized_similarity(o_lower, c_lower)
                    return "SPELL" if str_sim >= 0.65 else "OTHER"

                # geliyom -> geliyorum
                if next((True for m in o_last_group_morphemes if m.informal), False) and \
                        [m.mapped_morpheme if m.informal else m for m in o_last_group_morphemes] \
                        == c_last_group_morphemes:
                    return "ACCENT"

                # sozluk girdisi ayni -> fiilin koku ayni
                tag_ = "VERB:INFL"

                o_tenses = [m for m in o_last_group_morphemes if m.id_ in tenses]
                c_tenses = [m for m in c_last_group_morphemes if m.id_ in tenses]

                if o_tenses != c_tenses:
                    return tag_ + ":TENSE"

                o_sahis = {m for m in o_last_group_morphemes if m.id_ in kisi_ekleri}
                c_sahis = {m for m in c_last_group_morphemes if m.id_ in kisi_ekleri}

                if o_sahis == c_sahis:
                    # hem zaman kipleri hem de sahis kipleri ayniysa
                    # diger kipler hatali (yeterlilik, gereklilik, sart vb.)
                    return tag_ + ":KIP_CEKIMLERI"

                # VERB:INFL
                return tag_

            # if o_pos == c_pos:
            if c_pos in {PPOS.Conjunction, PPOS.PostPositive, PPOS.Punctuation, PPOS.Question, PPOS.Pronoun}:
                # eger kelimeler ayni degilse
                if o_toks[0].best_analysis.item != c_toks[0].best_analysis.item:
                    if c_pos == PPOS.Conjunction:
                        return "CONJ"
                    if c_pos == PPOS.PostPositive:
                        # burayi kontrol et
                        return "PREP"
                    if c_pos == PPOS.Punctuation:
                        return "PUNC"
                    if c_pos == PPOS.Question:
                        return "QUES"
                    if c_pos == PPOS.Pronoun:
                        return "PRON"

        # 2. SPELLING AND INFLECTION
        # Only check alphabetical strings on the corrected side
        if c_lower.isalpha():

            if c_lower not in spell:
                # Check if both sides have a common lemma
                if not c_toks[0].best_analysis.item.is_unknown():
                    # there is an analysis for original

                    c_last_group = c_toks[0].best_analysis.get_group(
                        len(c_toks[0].best_analysis.group_boundaries) - 1
                    )
                    c_last_pos = next(
                        (m.morpheme.id_ for m in c_last_group.morphemes if
                         m.morpheme.id_ in {'Noun', 'Verb', 'Adj', 'Adv'}),
                        None
                    )
                    if not o_toks[0].best_analysis.item.is_unknown():
                        # there is an analysis for the original

                        o_last_group = o_toks[0].best_analysis.get_group(
                            len(o_toks[0].best_analysis.group_boundaries) - 1
                        )

                        o_last_pos = next(
                            (m.morpheme.id_ for m in o_last_group.morphemes if
                             m.morpheme.id_ in {'Noun', 'Verb', 'Adj', 'Adv'}),
                            None
                        )

                        if o_toks[0].best_analysis.item == c_toks[0].best_analysis.item:
                            # they have the same root but different inflections
                            if o_last_pos == c_last_pos == 'VERB':
                                # both original and corrupt are verbs
                                return "VERB:INFL"

                        # they have different roots
                        o_last_morphemes = [m.morpheme for m in o_last_group.morphemes if m.morpheme.id_ != 'Zero']
                        c_last_morphemes = [m.morpheme for m in c_last_group.morphemes if m.morpheme.id_ != 'Zero']
                        if o_last_morphemes == c_last_morphemes:
                            # inflections are correct, however the roots are different
                            # it indicates a wrong usage of a verb or a noun
                            return c_last_pos.upper() if c_last_pos is not None else 'UNK'

                    # there is an analysis for corrected but no analysis for the original
                    # PROBABLY THE MOST COMMON SITUATION

                    # JUST A BASIC ASSUMPTION
                    # if the surface form of corrected's stem or corrected's root is the beginning of the original
                    starts_with_stem = o_str.startswith(c_toks[0].best_analysis.get_stem())
                    starts_with_root = o_str.startswith(c_toks[0].best_analysis.item.root)
                    if starts_with_stem or starts_with_root:
                        o_suffixes = o_str[len(c_toks[0].best_analysis.get_stem()):] if starts_with_stem else \
                            o_str[len(c_toks[0].best_analysis.item.root):]

                        # if suffixes are in Turkish suffix list it might be an inflection error
                        if o_suffixes in suffix:
                            if c_last_pos == 'VERB':
                                return "VERB:INFL"

                            if c_last_pos == 'NOUN':
                                return 'NOUN:INFL'

                # there is no analysis for neither orig nor corr

                str_sim = Levenshtein.normalized_similarity(tu.lower(o_str), tu.lower(c_str))

                # CHECK HOW THIS ASSUMPTION EFFECTS THE ACCURACY
                if str_sim > 0.55:
                    return "SPELL"

                if 0.33 <= str_sim < 0.55:
                    if len(o_str) <= 5 and len(c_str) <= 5:
                        return "SPELL"

                else:
                    return "OTHER"
        # 5. STRING SIMILARITY
        # These rules are quite language specific.
        if o_str.isalpha() and c_str.isalpha():
            # Normalised Lev distance works better than Lev ratio
            str_sim = Levenshtein.normalized_similarity(o_lower, c_lower)
            # WARNING: THIS IS AN APPROXIMATION.
            # Thresholds tuned manually on FCE_train + W&I_train
            # A. Short sequences are likely to be SPELL or function word errors
            if len(c_str) == 3:
                # bir -> bi
                if len(c_toks) == 2 and str_sim >= 0.6:
                    return "SPELL"
            if len(c_str) == 2:
                if 2 <= len(o_str) <= 3 and str_sim >= 0.5:
                    return "SPELL"

            # C. Longest sequences include MORPH errors
            if len(o_str) > 5 and len(c_str) > 5:
                if str_sim > 0.8:
                    return "SPELL"
        # Tricky cases
        else:
            return "OTHER"

    # Multi-token replacements (uncommon)

    o_last_groups = [
        o.best_analysis.get_group(len(o.best_analysis.group_boundaries) - 1) for o in o_toks
    ]
    c_last_groups = [
        o.best_analysis.get_group(len(o.best_analysis.group_boundaries) - 1) for o in c_toks
    ]

    o_last_pos = [
        next((m.morpheme.pos for m in g.morphemes if m.morpheme.pos in open_pos1), None) for g in o_last_groups
    ]

    c_last_pos = [
        next((m.morpheme.pos for m in g.morphemes if m.morpheme.pos in open_pos1), None) for g in c_last_groups
    ]

    if len(o_toks) == len(c_toks):
        # same number of tokens in both orig and corrupt

        # All same POS
        if len(set(o_last_pos + c_last_pos)) == 1:

            if o_last_pos[0] == PPOS.Noun and \
                    all(o.best_analysis.item.root == c.best_analysis.item.root for o, c in zip(o_toks, c_toks)):
                # if all are Noun and their roots are the same, this maybe a noun phrase error
                return "NOUN:PHRASE"

            if o_last_pos[0] in general_pos_set:
                return o_last_pos[0].short_form.upper()

        # The last pos is verb ; 'xx etmek/ yy olmak/ zz kılmak'
        if o_last_pos[-1] == PPOS.Verb:
            return "VERB"

    # Tricky cases.
    return "OTHER"


def noun_num_error(o_analysis: 'SentenceWordAnalysis', c_analysis: 'SentenceWordAnalysis'):
    """
    :param o_analysis: original sentence analysis
    :param c_analysis: corrected sentence analysis
    :return:
    """
    if o_analysis.best_analysis.item == c_analysis.best_analysis.item and not o_analysis.best_analysis.is_unknown():

        plural_found_in_o = next(
            (True for m in o_analysis.best_analysis.morpheme_data_list if m.morpheme.id_ in plural_morphemes),
            False
        )

        plural_found_in_c = next(
            (True for m in c_analysis.best_analysis.morpheme_data_list if m.morpheme.id_ in plural_morphemes),
            False
        )

        if (plural_found_in_o and not plural_found_in_c) or (plural_found_in_c and not plural_found_in_o):
            return True

        """ VERSIYON-1 Burayı tekrar değerlendirelim
        plural_morpheme_idx = next(
            (i for i, m in enumerate(o_analysis.morpheme_data_list) if m.morpheme.id_ in plural_morphemes),
            -1
        )
        if plural_morpheme_idx == -1:
            plural_morpheme_idx = next(
                (i for i, m in enumerate(c_analysis.morpheme_data_list) if m.morpheme.id_ in plural_morphemes),
                -1
            )

        
        if plural_morpheme_idx == -1:  # it means there is no plural morpheme assigned to either of the tokens
            return False

        
        i = 0
        while i < len(o_analysis.morpheme_data_list) and i < len(c_analysis.morpheme_data_list):
            if i < plural_morpheme_idx:
                if o_analysis.morpheme_data_list[i] != c_analysis.morpheme_data_list[i]:
                    return False
            else:  # i == plural_morpheme_idx
                return o_analysis.morpheme_data_list[i] == c_analysis.morpheme_data_list[i]

            i += 1
        """
    elif not c_analysis.best_analysis.is_unknown() and \
            o_analysis.word_analysis.inp.startswith(c_analysis.best_analysis.item.root):
        plural_found_in_c = next(
            (True for m in c_analysis.best_analysis.morpheme_data_list if m.morpheme.id_ in plural_morphemes),
            False
        )

        len_root = len(c_analysis.best_analysis.item.root)
        # search for 'ler', 'lar' suffixes in corrupt's suffixes
        plural_found_in_o = 'ler' in tu.lower(o_analysis.word_analysis.inp[len_root:]) or \
                            'lar' in tu.lower(o_analysis.word_analysis.inp[len_root:])

        if (plural_found_in_o and not plural_found_in_c) or (plural_found_in_c and not plural_found_in_o):
            return True

    return False


def verb_sva_error(o_analysis: 'SentenceWordAnalysis', c_analysis: 'SentenceWordAnalysis') -> bool:
    """
    parameters are interchangeable
    :param o_analysis: original sentence analysis
    :param c_analysis: corrected sentence analysis
    :return:
    """
    last_group_morphs_o = o_analysis.best_analysis.get_group(len(o_analysis.best_analysis.group_boundaries) - 1)
    last_group_morphs_c = c_analysis.best_analysis.get_group(len(c_analysis.best_analysis.group_boundaries) - 1)

    is_verb = False
    o_passive = False
    o_kisi_eki = None
    for m in last_group_morphs_o.morphemes:

        if m.morpheme.id_ == 'Pass':
            o_passive = True
        if m.morpheme.pos == PPOS.Verb:
            is_verb = True

        if is_verb:
            if m.morpheme.id_ in kisi_ekleri:
                o_kisi_eki = m.morpheme.id_

    is_verb = False
    c_kisi_eki = None
    c_passive = False
    for m in last_group_morphs_c.morphemes:

        if m.morpheme.id_ == 'Pass':
            c_passive = True
        if m.morpheme.pos == PPOS.Verb:
            is_verb = True

        if is_verb:
            if m.morpheme.id_ in kisi_ekleri:
                c_kisi_eki = m.morpheme.id_

    if (not (o_passive ^ c_passive)) and (o_kisi_eki is not None and c_kisi_eki is not None):
        return o_kisi_eki != c_kisi_eki

    return False


def diacritization_error(o_str: str, c_str: str):
    """

    :param o_str: original sentence
    :param c_str: corrected sentence
    :return:
    """
    for i, c in enumerate(c_str):
        # if the character is turkish specific and the character in corrupt at the same position is not the same
        # with the original character check for string equality while ignoring diacritics
        if tu.TR_ALPH.is_turkish_specific(c) and i < len(o_str) and c != o_str[i]:
            return tu.TR_ALPH.equals_ignore_diacritics(o_str, c_str)

    return False


# Input 1: Spacy orig tokens
# Input 2: Spacy cor tokens
# Output: Boolean; the difference between orig and cor is only whitespace or case
def only_orth_change(o_toks: Sequence['SentenceWordAnalysis'], c_toks: Sequence['SentenceWordAnalysis']):
    o_join = "".join([tu.lower(o.word_analysis.inp) for o in o_toks])
    c_join = "".join([tu.lower(c.word_analysis.inp) for c in c_toks])
    if o_join == c_join:
        return True
    return False


# Input 1: Spacy orig tokens
# Input 2: Spacy cor tokens
# Output: Boolean; the tokens are exactly the same but in a different order
def exact_reordering(o_toks: Sequence['SentenceWordAnalysis'], c_toks: Sequence['SentenceWordAnalysis']):
    # Sorting lets us keep duplicates.
    o_set = sorted([tu.lower(o.word_analysis.inp) for o in o_toks])
    c_set = sorted([tu.lower(c.word_analysis.inp) for c in c_toks])
    if o_set == c_set:
        return True
    return False
