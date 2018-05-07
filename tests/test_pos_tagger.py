# coding: utf-8
from __future__ import unicode_literals
from spacy_lefff import POSTagger, LefffLemmatizer

import pytest
import spacy

@pytest.fixture
def nlp():
    nlp = spacy.load('fr')
    french_pos_tagger = POSTagger()
    nlp.add_pipe(french_pos_tagger, after='parser')
    return nlp

@pytest.fixture
def add_lefff_lemma_nlp(nlp):
    french_lemmatizer = LefffLemmatizer(melt=True)
    nlp.add_pipe(french_lemmatizer, after='POSTagger')
    return nlp

def test_sentence_one(nlp):
    tokens = nlp(u"Il y a des Costariciennes.")
    assert tokens[0]._.melt_tagger == 'CLS'
    assert tokens[1]._.melt_tagger == 'CLO'
    assert tokens[2]._.melt_tagger == 'V'
    assert tokens[3]._.melt_tagger == 'DET'
    assert tokens[4]._.melt_tagger == 'NPP'
    assert tokens[5]._.melt_tagger == 'PONCT'

def test_sentence_lefff_pos_lemma(add_lefff_lemma_nlp):
    tokens = add_lefff_lemma_nlp(u"Qu'est ce qu'il se passe")
    assert True
