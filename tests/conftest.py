import pytest
import spacy
import os
from spacy_lefff import POSTagger, LefffLemmatizer
from spacy_lefff.melt_tagger import DATA_DIR, PACKAGE


@pytest.fixture(scope='session')
def nlp():
    nlp = spacy.load('fr_core_news_sm')
    french_lemmatizer = LefffLemmatizer()
    nlp.add_pipe(french_lemmatizer, after='parser')
    return nlp


@pytest.fixture(scope='session')
def nlp_pos():
    nlp = spacy.load('fr_core_news_sm')
    french_pos_tagger = POSTagger()
    nlp.add_pipe(french_pos_tagger, name='POSTagger', after='parser')
    return nlp


@pytest.fixture(scope='session')
def add_lefff_lemma_nlp(nlp_pos):
    french_lemmatizer = LefffLemmatizer(after_melt=True)
    nlp_pos.add_pipe(french_lemmatizer, after='POSTagger')
    return nlp_pos

@pytest.fixture(scope='session')
def model_dir():
    return os.path.join(DATA_DIR, PACKAGE, 'models/fr')