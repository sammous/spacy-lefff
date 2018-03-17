# coding: utf-8
from __future__ import unicode_literals

import pytest

import spacy
from spacy_lefff import LefffLemmatizer

@pytest.fixture(scope='function')
def nlp():
    lang = 'fr'
    pipeline = ['tagger', 'parser', 'ner']
    cls = spacy.util.get_lang_class(lang)
    nlp = cls()
    for name in pipeline:
        component = nlp.create_pipe(name)
        nlp.add_pipe(component)
    french_lemmatizer = LefffLemmatizer()
    nlp.add_pipe(french_lemmatizer, after='parser')
    return nlp

"""
Test suite coming from spacy.
Link: https://github.com/explosion/spaCy
/blob/master/spacy/tests/lang/fr/test_lemmatization.py
"""

def test_lemmatizer_verb():
    nlp = spacy.load('fr')
    french_lemmatizer = LefffLemmatizer()
    nlp.add_pipe(french_lemmatizer, after='parser')
    tokens = nlp(u"Qu'est-ce que tu fais?")

    assert tokens[0].lemma_ == "que"
    assert tokens[1].lemma_ == "être"
    assert tokens[5].lemma_ == "faire"


@pytest.mark.xfail(reason="sont tagged as AUX")
def test_lemmatizer_noun_verb_2():
    nlp = spacy.load('fr')
    french_lemmatizer = LefffLemmatizer()
    nlp.add_pipe(french_lemmatizer, after='parser')
    tokens = nlp(u"Les abaissements de température sont gênants.")
    assert tokens[4].lemma_ == "être"


@pytest.mark.xfail(reason="Costaricienne TAG is PROPN instead of NOUN and spacy don't lemmatize PROPN")
def test_lemmatizer_noun():
    nlp = spacy.load('fr')
    french_lemmatizer = LefffLemmatizer()
    nlp.add_pipe(french_lemmatizer, after='parser')
    tokens = nlp(u"il y a des Costaricienne.")
    assert tokens[4].lemma_ == "Costaricain"

def test_lemmatizer_noun_2():
    nlp = spacy.load('fr')
    french_lemmatizer = LefffLemmatizer()
    nlp.add_pipe(french_lemmatizer, after='parser')
    tokens = nlp(u"Les abaissements de température sont gênants.")
    assert tokens[1].lemma_ == "abaissement"
    assert tokens[5].lemma_ == "gênant"
