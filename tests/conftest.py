import pytest
import spacy
import os
from spacy.language import Language
from spacy_lefff import POSTagger, LefffLemmatizer
from spacy_lefff.melt_tagger import DATA_DIR, PACKAGE


@Language.factory('french_lemmatizer')
def create_french_lemmatizer(nlp, name):
    return LefffLemmatizer()

@Language.factory('french_lemmatizer_after_melt')
def create_french_lemmatizer_with_melt(nlp, name):
    return LefffLemmatizer(after_melt=True)

@Language.factory('melt_tagger')
def create_melt_tagger(nlp, name):
    return POSTagger()

@pytest.fixture(scope='session')
def nlp():
    nlp = spacy.load('fr_core_news_sm')
    nlp.add_pipe('french_lemmatizer', after='parser')
    return nlp


@pytest.fixture(scope='session')
def nlp_pos():
    nlp = spacy.load('fr_core_news_sm')
    nlp.add_pipe('melt_tagger', after='parser')
    return nlp


@pytest.fixture(scope='session')
def add_lefff_lemma_nlp(nlp_pos):
    nlp_pos.add_pipe('french_lemmatizer_after_melt', after='melt_tagger')
    return nlp_pos

@pytest.fixture(scope='session')
def model_dir():
    return os.path.join(DATA_DIR, PACKAGE, 'models/fr')