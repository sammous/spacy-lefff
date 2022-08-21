# coding: utf-8
import pytest

import spacy
from spacy_lefff import LefffLemmatizer

"""
Test suite coming from spacy.
Link: https://github.com/explosion/spaCy
/blob/master/spacy/tests/lang/fr/test_lemmatization.py
"""


def test_lemmatizer_verb(nlp):
    tokens = nlp("J'ai une maison à Paris.")
    assert tokens[1]._.lefff_lemma == "avoir"


def test_lemmatizer_noun_verb(nlp):
    tokens = nlp("Les abaissements de température sont gênants.")
    assert tokens[1]._.lefff_lemma == "abaissement"


def test_lemmatizer_noun(nlp):
    tokens = nlp("il y a des Françaises.")
    assert tokens[4]._.lefff_lemma == "français"


def test_lemmatizer_noun_2(nlp):
    tokens = nlp("Les abaissements de température sont gênants.")
    assert tokens[1]._.lefff_lemma == "abaissement"
    assert tokens[3]._.lefff_lemma == "température"


def test_punctuations(nlp):
    tokens = nlp(". ?")
    assert tokens[0]._.lefff_lemma == "."
    assert tokens[1]._.lefff_lemma == "?"


@pytest.mark.exception
def test_lemmatizer_exception():
    french_lemmatizer = LefffLemmatizer()
    assert french_lemmatizer.lemmatize("unknow34", "unknown") is None


def test_lemmatizer_default():
    french_lemmatizer = LefffLemmatizer(default=True)
    assert french_lemmatizer.lemmatize("Apple", "NOUN") == "apple"
