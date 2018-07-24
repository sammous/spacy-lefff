# coding: utf8

import os
import logging
import io

from spacy.tokens import Token
from .mappings import SPACY_LEFFF_DIC

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
LEFFF_FILE_NAME = 'lefff-3.4.mlex'
LOGGER = logging.getLogger(__name__)


class LefffLemmatizer(object):
    """
    Lefff Lemmatizer based on Lefff's extension file .mlex

    Sagot (2010). The Lefff, a freely available and large-coverage
    morphological and syntactic lexicon for French.
    In Proceedings of the 7th international conference on Language Resources
    and Evaluation (LREC 2010), Istanbul, Turkey
    """

    name = 'lefff_lemma'

    def __init__(self, data_dir=DATA_DIR,
                 lefff_file_name=LEFFF_FILE_NAME, after_melt=False):
        LOGGER.info('New LefffLemmatizer instantiated.')
        # register your new attribute token._.lefff_lemma
        if not Token.get_extension(self.name):
            Token.set_extension(self.name, default=None)
        else:
            LOGGER.info('Token {} already registered'.format(self.name))
        # In memory lemma mapping
        self.lemma_dict = {}
        self.after_melt = after_melt
        with io.open(os.path.join(data_dir, lefff_file_name),
                     encoding='utf-8') as lefff_file:
            LOGGER.info('Reading lefff data...')
            for line in lefff_file:
                els = line.split('\t')
                self.lemma_dict[(els[0], els[1])] = els[2]
        LOGGER.info('Successfully loaded lefff lemmatizer')

    def lemmatize(self, text, pos):
        text = text.lower() if pos != 'PROPN' else text
        try:
            if self.after_melt:
                return self.lemma_dict[(text, pos)]
            else:
                if (pos in SPACY_LEFFF_DIC) and (
                        (text, SPACY_LEFFF_DIC[pos]) in self.lemma_dict):
                    return self.lemma_dict[(text, SPACY_LEFFF_DIC[pos])]
        except BaseException:
            # if nothing was matched in leff lemmatizer, notify it
            return None

    def __call__(self, doc):
        for token in doc:
            t = token._.melt_tagger.lower() if self.after_melt else token.pos_
            lemma = self.lemmatize(token.text, t)
            token._.lefff_lemma = lemma
        return doc
