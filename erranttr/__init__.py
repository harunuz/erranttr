from importlib import import_module

from erranttr.annotator import Annotator

# ERRANT version
__version__ = '0.1.0'


# Load an ERRANT Annotator object for a given language
def load(lang):
    # Make sure the language is supported
    supported = {"tr"}
    if lang not in supported:
        raise Exception("%s is an unsupported or unknown language" % lang)

    # Load language edit merger
    merger = import_module("erranttr.%s.merger" % lang)

    # Load language edit classifier
    classifier = import_module("erranttr.%s.classifier" % lang)
    # The English classifier needs spacy

    # Return a configured ERRANT annotator
    return Annotator(lang, merger, classifier)
