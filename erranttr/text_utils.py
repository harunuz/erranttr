from zemberek.core.turkish.turkish_alphabet import TurkishAlphabet

TR_ALPH = TurkishAlphabet.INSTANCE

asciification_map = {
    ord(u"ı"): ord(u"i"), ord(u"ç"): ord(u"c"), ord(u"ş"): ord(u"s"),
    ord(u"ü"): ord(u"u"), ord(u"ö"): ord(u"o"), ord(u"ğ"): ord(u"g"),
    ord(u"İ"): ord(u"I"), ord(u"Ç"): ord(u"C"), ord(u"Ş"): ord(u"S"),
    ord(u"Ü"): ord(u"U"), ord(u"Ö"): ord(u"O"), ord(u"Ğ"): ord(u"G"),
}

diacritization_map = {v: k for k, v in asciification_map.items()}

diacritics = ('ı', "ö", "ü", "ş", "ç", "ğ", "İ", "Ö", "Ü", "Ğ", "Ç", "Ş")


def lower(text: str) -> str:
    return text.translate(TR_ALPH.lower_map).lower()


def upper(text: str) -> str:
    return text.translate(TR_ALPH.upper_map).upper()
