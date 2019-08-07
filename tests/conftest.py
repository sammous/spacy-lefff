import pytest
import spacy
from spacy_lefff import POSTagger, LefffLemmatizer


@pytest.fixture(scope='session')
def nlp():
    nlp = spacy.load('fr')
    french_lemmatizer = LefffLemmatizer()
    nlp.add_pipe(french_lemmatizer, after='parser')
    return nlp


@pytest.fixture(scope='session')
def nlp_pos():
    nlp = spacy.load('fr')
    french_pos_tagger = POSTagger()
    nlp.add_pipe(french_pos_tagger, name='POSTagger', after='parser')
    return nlp


@pytest.fixture(scope='session')
def add_lefff_lemma_nlp(nlp_pos):
    french_lemmatizer = LefffLemmatizer(after_melt=True)
    nlp_pos.add_pipe(french_lemmatizer, after='POSTagger')
    return nlp_pos
