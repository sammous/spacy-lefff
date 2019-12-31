# coding: utf8

import os
import logging
import io

from spacy.tokens import Token
from .mappings import SPACY_LEFFF_DIC, MELT_TO_LEFFF_DIC

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
LEFFF_FILE_NAME = 'lefff-3.4.mlex'
LOGGER = logging.getLogger(__name__)


class POSNotFoundError(KeyError):
    """Raised when no lemma was found"""
    pass


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
                 lefff_file_name=LEFFF_FILE_NAME,
                 after_melt=False,
                 default=False):
        LOGGER.info('New LefffLemmatizer instantiated.')
        # register your new attribute token._.lefff_lemma
        if not Token.get_extension(self.name):
            Token.set_extension(self.name, default=None)
        else:
            LOGGER.info('Token {} already registered'.format(self.name))
        # In memory lemma mapping
        self.lemma_dict = {}
        self.after_melt = after_melt
        self.default = default
        with io.open(os.path.join(data_dir, lefff_file_name),
                     encoding='utf-8') as lefff_file:
            LOGGER.info('Reading lefff data...')
            for line in lefff_file:
                els = line.split('\t')
                self.lemma_dict[(els[0], els[1])] = els[2]
        LOGGER.info('Successfully loaded lefff lemmatizer')

    def lemmatize(self, text, pos, from_melt=False):
        text = text.lower() if pos != 'PROPN' else text
        try:
            if from_melt:
                if pos in MELT_TO_LEFFF_DIC:
                    pos = MELT_TO_LEFFF_DIC[pos]
                return self.lemma_dict[(text, pos)]
            else:
                if (pos in SPACY_LEFFF_DIC) and (
                        (text, SPACY_LEFFF_DIC[pos]) in self.lemma_dict):
                    return self.lemma_dict[(text, SPACY_LEFFF_DIC[pos])]
                else:
                    raise POSNotFoundError
        except:
            # if nothing was matched in leff lemmatizer, notify it
            if self.default:
                return text
            return None

    def __call__(self, doc):
        for token in doc:
            from_melt = False
            if self.after_melt and token._.melt_tagger:
                from_melt = True
                t = token._.melt_tagger.lower()
            else:
                t = token.pos_
            lemma = self.lemmatize(token.text, t, from_melt)
            token._.lefff_lemma = lemma
        return doc
