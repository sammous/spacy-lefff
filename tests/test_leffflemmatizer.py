# coding: utf-8
from __future__ import unicode_literals

import pytest

import spacy
from spacy_lefff import LefffLemmatizer

"""
Test suite coming from spacy.
Link: https://github.com/explosion/spaCy
/blob/master/spacy/tests/lang/fr/test_lemmatization.py
"""

@pytest.fixture
def nlp():
    nlp = spacy.load('fr')
    french_lemmatizer = LefffLemmatizer()
    nlp.add_pipe(french_lemmatizer, after='parser')
    return nlp

def test_lemmatizer_verb(nlp):
    tokens = nlp(u"J'ai une maison à Paris.")
    assert tokens[1]._.lefff_lemma == "avoir"

def test_lemmatizer_noun_verb(nlp):
    tokens = nlp(u"Les abaissements de température sont gênants.")
    assert tokens[1]._.lefff_lemma == "abaissement"

def test_lemmatizer_noun(nlp):
    tokens = nlp(u"il y a des Françaises.")
    for d in tokens:
        print(d.text, d.pos_, d._.lefff_lemma, d.tag_)
    assert tokens[4]._.lefff_lemma == "français"

def test_lemmatizer_noun_2(nlp):
    tokens = nlp(u"Les abaissements de température sont gênants.")
    assert tokens[1]._.lefff_lemma == "abaissement"
    assert tokens[3]._.lefff_lemma == "température"

def test_punctuations(nlp):
    tokens = nlp(u". ?")
    assert tokens[0]._.lefff_lemma == "."
    assert tokens[1]._.lefff_lemma == "?"

def test_lemmatizer_exception():
    french_lemmatizer = LefffLemmatizer()
    assert french_lemmatizer.lemmatize("unknow", "unknown") is None
