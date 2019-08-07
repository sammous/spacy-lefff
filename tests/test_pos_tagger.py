# coding: utf-8

from spacy_lefff import POSTagger, LefffLemmatizer
from spacy_lefff.melt_tagger import MODELS_DIR

import pytest
import spacy
import os


def test_sentence_one(add_lefff_lemma_nlp):
    tokens = add_lefff_lemma_nlp(u"Il y a des Costariciennes.")
    assert tokens[0]._.melt_tagger == 'CLS'
    assert tokens[1]._.melt_tagger == 'CLO'
    assert tokens[2]._.melt_tagger == 'V'
    assert tokens[3]._.melt_tagger == 'DET'
    assert tokens[4]._.melt_tagger == 'NPP'
    assert tokens[5]._.melt_tagger == 'PONCT'


def test_sentence_lefff_pos_lemma(add_lefff_lemma_nlp):
    tokens = add_lefff_lemma_nlp(u"Qu'est ce qu'il se passe")


def test_lemmatizer_verb(add_lefff_lemma_nlp):
    tokens = add_lefff_lemma_nlp(u"J'ai une maison à Paris.")
    assert tokens[1]._.lefff_lemma == u"avoir"
    assert tokens[2]._.lefff_lemma == u"un"


def test_lemmatizer_noun(add_lefff_lemma_nlp):
    tokens = add_lefff_lemma_nlp(u"il y a des Françaises.")
    assert tokens[4]._.lefff_lemma == u"français"
    assert tokens[3]._.lefff_lemma == u"un"


def test_load_lexicon():
    french_pos_tagger = POSTagger()
    lex_dict = french_pos_tagger.lex_dict
    lexicon = os.path.join(MODELS_DIR, 'lexicon.json')
    french_pos_tagger.load_lexicon(lexicon)
    assert french_pos_tagger.lex_dict == lex_dict


def test_load_tag():
    french_pos_tagger = POSTagger()
    tag_dict = french_pos_tagger.tag_dict
    tag = os.path.join(MODELS_DIR, 'tag_dict.json')
    french_pos_tagger.load_lexicon(tag)
    assert french_pos_tagger.tag_dict == tag_dict
