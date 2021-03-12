#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################################
# Copyright (C) 2009 Pascal Denis and Benoit Sagot
##
# This library is free software; you can redistribute it and#or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
##
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
##########################################################################

import os
import sys
import re
import math
import tempfile
import codecs
import operator
import time
import optparse
import unicodedata
import subprocess
from collections import defaultdict
import logging

WD_TAG_RE = re.compile(r'^(.+)/([^\/]+)$')
CAPONLYLINE_RE = re.compile(r'^([^a-z]+)$')
number = re.compile("\d")
hyphen = re.compile("\-")
equals = re.compile("=")
upper = re.compile("^([A-Z]|[^_].*[A-Z])")
allcaps = re.compile("^[A-Z]+$")

import numpy as np

from json import dumps, loads
import io
from spacy.tokens import Token as tk
from .lefff import LefffLemmatizer
from .downloader import Downloader

LOGGER = logging.getLogger(__name__)

PACKAGE = 'tagger'
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

URL_MODEL = 'https://github.com/sammous/spacy-lefff-model/releases/latest/download/model.tar.gz'

# extra options dict for feature selection
feat_select_options = {
    # previous default values
    # 'win':2, # context window size
    # 'pwin':2, # context window size for predicted tags (left context)
    # 'lex_wd':1, # lefff current word features
    # 'lex_lhs':1, # lefff LHS context features
    # 'lex_rhs':1, # lefff RHS context features
    # 'pln':4,
    # 'sln':4,
    # 'rpln':1,
    # 'rsln':0,
    # 'ffthrsld':2, # min feat occ: will discard any features occurring (strictly) less than ffthrsld times in the training data
    # 'norm':0, # normalization (0=none, 1=L1, 2=L2)
    # new default values (Sagot HDR)
    'win': 2,  # context window size
    'pwin': 2,  # context window size for predicted tags (left context)
    'lex_wd': 1,  # lefff current word features
    'lex_lhs': 1,  # lefff LHS context features
    'lex_rhs': 1,  # lefff RHS context features
    'pln': 4,
    'sln': 5,
    'rpln': 3,
    'rsln': 3,
    'ffthrsld': 1,  # min feat occ: will discard any features occurring (strictly) less than ffthrsld times in the training data
    'norm': 0,  # normalization (0=none, 1=L1, 2=L2)
}

############################ pos_tagger.py ############################


class POSTagger(Downloader):

    name = 'melt_tagger'
    
    def __init__(
            self,
            data_dir=DATA_DIR,
            model_dir_path=None,
            lexicon_file_path=None,
            tag_file_path=None,
            package=PACKAGE,
            url=URL_MODEL,
            print_probas=False):
        super(
            POSTagger,
            self).__init__(
            package,
            url=url,
            download_dir=data_dir)
        if not tk.get_extension(self.name):
            tk.set_extension(self.name, default=None)
        else:
            LOGGER.info('Token {} already registered'.format(self.name))

        model_dir_path = model_dir_path if model_dir_path else os.path.join(data_dir, package, 'models/fr')
        lexicon_file_path = lexicon_file_path if lexicon_file_path else os.path.join(model_dir_path, 'lexicon.json')
        tag_file_path = tag_file_path if tag_file_path else os.path.join(model_dir_path, 'tag_dict.json')

        LOGGER.info("  TAGGER: Loading lexicon...")
        self.lex_dict = unserialize(lexicon_file_path)
        LOGGER.info("  TAGGER: Loading tags...")
        self.tag_dict = unserialize(tag_file_path)
        self.classifier = MaxEntClassifier()
        self.cache = {}
        self._load_model(model_dir_path)
        # print the probability of the tag along to the tag itself
        self.print_probas = print_probas
        return

    def _load_model(self, model_path):
        try:
            self.classifier.load(model_path)
        except Exception as e:
            sys.exit(
                "Error: Failure load POS model from %s (%s)" %
                (model_path, e))
        return

    def tag_token_sequence(
            self,
            tokens,
            feat_options=feat_select_options,
            beam_size=3):
        ''' N-best breath search for the best tag sequence for each sentence'''
        # maintain N-best sequences of tagged tokens
        sequences = [([], 0.0)]  # log prob.
        for i, token in enumerate(tokens):
            n_best_sequences = []
            # cache static features
            cached_inst = Instance(label=tokens[i].label,
                                   index=i, tokens=tokens,
                                   feat_selection=feat_options,
                                   lex_dict=self.lex_dict,
                                   tag_dict=self.tag_dict,
                                   cache=self.cache)
            cached_inst.get_static_features()
            # get possible tags: union of tags found in tag_dict and
            # lex_dict
            wd = token.string
            wasCap = token.wasCap
            legit_tags1 = self.tag_dict.get(wd, {})
            legit_tags2 = self.lex_dict.get(wd, {})
#            legit_tags2 = {} # self.lex_dict.get(wd,{})
#            print >> sys.stderr, "legit_tags1: ", [t for t in legit_tags1]
            for j, seq in enumerate(sequences):
                seq_j, log_pr_j = sequences[j]
                tokens_j = seq_j + tokens[i:]  # tokens with previous labels
                # classify token
                inst = Instance(label=tokens[i].label,
                                index=i, tokens=tokens_j,
                                feat_selection=feat_options,
                                lex_dict=self.lex_dict,
                                tag_dict=self.tag_dict,
                                cache=self.cache)
                inst.fv = cached_inst.fv[:]
                inst.get_sequential_features()
                label_pr_distrib = self.classifier.class_distribution(inst.fv)
                # extend sequence j with current token
                for (cl, pr) in label_pr_distrib:
                    # make sure that cl is a legal tag
                    if legit_tags1 or legit_tags2:
                        if (cl not in legit_tags1) and (cl not in legit_tags2):
                            continue
                    labelled_token = Token(
                        string=token.string,
                        pos=token.pos,
                        comment=token.comment,
                        wasCap=wasCap,
                        label=cl,
                        proba=pr,
                        label_pr_distrib=label_pr_distrib)
                    n_best_sequences.append(
                        (seq_j + [labelled_token], log_pr_j + math.log(pr)))
            # sort sequences
            n_best_sequences.sort(key=operator.itemgetter(1))
            # debug_n_best_sequence(n_best_sequences)
            # keep N best
            sequences = n_best_sequences[-beam_size:]
        # return sequence with highest prob.
        best_sequence = sequences[-1][0]
        # print >> sys.stderr, "Best tok seq:", [(t.string,t.label) for t in best_sequence]
        return best_sequence

    def __call__(
            self,
            doc,
            handle_comments=False,
            feat_options=feat_select_options,
            beam_size=3,
            lowerCaseCapOnly=False,
            zh_mode=False):
        LOGGER.info("  TAGGER: POS Tagging...")
        t0 = time.time()
        # process sentences
        s_ct = 0
        if (handle_comments):
            comment_re = re.compile(r'^{.*} ')
            split_re = re.compile(r'(?<!\}) ')
            token_re = re.compile(r'(?:{[^}]*} *)?[^ ]+')
        else:
            split_re = re.compile(r' ')
            token_re = re.compile(r'[^ ]+')
        line = " ".join([w.text for w in doc])
        wasCapOnly = 0
        if (lowerCaseCapOnly and len(line) > 10):
            wasCapOnly = CAPONLYLINE_RE.match(line)
        if (wasCapOnly):
            wasCapOnly = 1
        else:
            wasCapOnly = 0
        if (wasCapOnly):
            line = line.lower()
#                LOGGER.info( "CAPONLY: "+line
        wds = []
#            wds = split_re.split(line)
        result = token_re.match(line)
        while (result):
            wds.append(result.group())
            line = token_re.sub("", line, 1)
            line = line.strip(' \n')
            result = token_re.match(line)
        tokens = []
        for wd in wds:
            token = Token(string=wd, wasCap=wasCapOnly)
            tokens.append(token)
        tagged_tokens = self.tag_token_sequence(tokens,
                                                feat_options=feat_options,
                                                beam_size=beam_size)
        if (self.print_probas):
            tagged_sent = " ".join([tok.__pstr__() for tok in tagged_tokens])
        else:
            tagged_sent = " ".join([tok.__str__() for tok in tagged_tokens])
        for w, t in zip(doc, tagged_tokens):
            w._.melt_tagger = t.label
        return doc

    def load_tag_dictionary(self, filepath):
        LOGGER.info("  TAGGER: Loading tag dictionary...")
        self.tag_dict = unserialize(filepath)
        LOGGER.info("  TAGGER: Loading tag dictionary: done")
        return

    def load_lexicon(self, filepath):
        LOGGER.info("  TAGGER: Loading external lexicon...")
        self.lex_dict = unserialize(filepath)
        LOGGER.info("  TAGGER: Loading external lexicon: done")
        return


############################ my_token.py ############################


class Token:

    def __init__(
            self,
            string=None,
            wasCap=0,
            pos=None,
            label=None,
            proba=None,
            comment=None,
            label_pr_distrib=[],
            index=None,
            position=None):
        if isinstance(
                string,
                tuple) and isinstance(
                string[2],
                sxp.Token):  # DAG
            self.string = string[2].forme
            self.position = tuple(string[0:2])
            self.tokobj = string[2]
        elif isinstance(string, Token):
            self.string = string.string
            self.position = string.position
            self.tokobj = string.tokobj
        else:
            self.position = position
            self.string = string
            self.comment = comment
        self.index = index
        self.wasCap = wasCap
        self.pos = pos
        self.label = label
        self.proba = proba
        self.comment = comment
        self.label_pr_distrib = label_pr_distrib
        if (self.comment is None):
            self.comment = ""
        return

    def set_label(self, label):
        self.label = label
        return

    def __str__(self):
        if hasattr(self, 'tokobj'):
            r = ""
            if self.tokobj.commentaire != "":
                r += "{%s} " % (self.tokobj.commentaire,)
            r += "%s__%s" % (self.string, self.label)
            if self.tokobj.semantique != "":
                r += "[|%s|] " % (self.tokobj.semantique,)
            return r
        if (self.wasCap):
            return "%s%s/%s" % (self.comment, self.string.upper(), self.label)
        else:
            return "%s%s/%s" % (self.comment, self.string, self.label)

    def __pstr__(self):
        if (self.wasCap):
            return "%s%s/%s/%s" % (self.comment,
                                   self.string.upper(),
                                   self.label,
                                   self.proba)
        else:
            return "%s%s/%s/%s" % (self.comment,
                                   self.string, self.label, self.proba)


############################ classifier.py ############################


class MaxEntClassifier:

    def __init__(self):
        self.classes = []
        self.feature2int = {}
        self.weights = np.zeros((0, 0))
        self.bias_weights = np.zeros((0, 0))
        return

    def load(self, dirpath):
        LOGGER.info("  TAGGER: Loading model from %s..." % dirpath)
        self.classes = unserialize(os.path.join(dirpath, 'classes.json'))
        self.feature2int = unserialize(
            os.path.join(dirpath, 'feature_map.json'))
        self.weights = np.load(
            os.path.join(
                dirpath,
                'weights.npy'),
            allow_pickle=True,
            encoding='latin1')
        self.bias_weights = np.load(
            os.path.join(
                dirpath,
                'bias_weights.npy'),
            allow_pickle=True,
            encoding='latin1')
        LOGGER.info("  TAGGER: Loading model from %s: done" % dirpath)
        return

    def dump(self, dirpath):
        LOGGER.info("  TAGGER (TRAIN): Dumping model in %s..." % dirpath)
        serialize(self.classes, os.path.join(dirpath, 'classes.json'))
        serialize(self.feature2int, os.path.join(dirpath, 'feature_map.json'))
        self.weights.dump(os.path.join(dirpath, 'weights.npy'))
        self.bias_weights.dump(os.path.join(dirpath, 'bias_weights.npy'))
        LOGGER.info("  TAGGER (TRAIN): Dumping model in %s: done." % dirpath)
        return

    def categorize(self, features):
        """ sum over feature weights and return class that receives
        highest overall weight
        """
        weights = self.bias_weights
        for f in features:
            fint = self.feature2int.get(f, None)
            if not fint:
                continue
            fweights = self.weights[fint]
            # summing bias and fweights
            weights = weights + fweights
        # find highest weight sum
        best_weight = weights.max()
        # return class corresponding to highest weight sum
        best_cl_index = np.nonzero(weights == best_weight)[0][0]
        return self.classes[best_cl_index]

    def class_distribution(self, features):
        """ probability distribution over the different classes
        """
        # print >> sys.stderr, "event: %s" % features
        weights = self.bias_weights
        for f in features:
            fint = self.feature2int.get(f, None)
            if fint is None:
                continue
            fweights = self.weights[fint]
            # summing bias and fweights
            weights = weights + fweights
        # exponentiation of weight sum
        scores = list(map(math.exp, list(weights)))
        # compute normalization constant Z
        z = sum(scores)
        # compute probabilities
        probs = [s / z for s in scores]
        # return class/prob map
        return list(zip(self.classes, probs))


############################ instance.py ############################


class Instance:

    def __init__(self, index, tokens, label=None, lex_dict={}, tag_dict={},
                 feat_selection={}, cache={}):
        self.label = label
        self.fv = []
        self.feat_selection = feat_selection
        # token
        self.token = tokens[index]
        self.index = index
        self.word = self.token.string
        # lexicons
        self.lex_dict = lex_dict
        self.tag_dict = tag_dict
        self.cache = cache  # TODO
        # contexts
        win = feat_selection.get('win', 2)
        pwin = feat_selection.get('pwin', 2)
        self.context_window = win
        self.ptag_context_window = pwin
        self.set_contexts(tokens, index, win, pwin)
        return

    def set_contexts(self, toks, idx, win, pwin):
        rwin = win
        lwin = max(win, pwin)
        lconx = toks[:idx][-lwin:]
        rconx = toks[idx + 1:][:rwin]
        self.left_wds = [tok.string for tok in lconx]
        if len(self.left_wds) < lwin:
            self.left_wds = ["<s>"] + self.left_wds
        self.left_labels = [tok.label for tok in lconx]
        self.right_wds = [tok.string for tok in rconx]
        if len(self.right_wds) < rwin:
            self.right_wds += ["</s>"]
        self.lex_left_tags = {}
        self.lex_right_tags = {}
        if self.lex_dict:
            self.lex_left_tags = [
                "|".join(
                    list(
                        self.lex_dict.get(
                            tok.string, {
                                "unk": 1}).keys())) for tok in lconx if tok is not None]
            self.lex_right_tags = [
                "|".join(
                    list(
                        self.lex_dict.get(
                            tok.string, {
                                "unk": 1}).keys())) for tok in rconx if tok is not None]
        if self.tag_dict:
            self.train_left_tags = [
                "|".join(
                    list(
                        self.tag_dict.get(
                            tok.string, {
                                "unk": 1}).keys())) for tok in lconx if tok is not None]
            self.train_right_tags = [
                "|".join(
                    list(
                        self.tag_dict.get(
                            tok.string, {
                                "unk": 1}).keys())) for tok in rconx if tok is not None]
        return

    def add(self, name, key, value=-1):
        if value == -1:
            f = '%s=%s' % (name, key)
        else:
            f = '%s=%s=%s' % (name, key, value)
        self.fv.append(f)
        return f

    def add_cached_feats(self, features):
        self.fv.extend(features)
        return

    def __str__(self):
        return '%s\t%s' % (self.label, " ".join(self.fv))

    def weighted_str(self, w):
        return '%s $$$WEIGHT %f\t%s' % (self.label, w, " ".join(self.fv))

    def get_features(self):
        self.get_static_features()
        self.get_sequential_features()
        return

    def get_sequential_features(self):
        ''' features based on preceding tagging decisions '''
        prev_labels = self.left_labels
        for n in range(1, self.ptag_context_window + 1):
            if len(prev_labels) >= n:
                # unigram for each position
                if n == 1:
                    unigram = prev_labels[-n]
                else:
                    unigram = prev_labels[-n:-n + 1][0]
                self.add('ptag-%s' % n, unigram)
                if n > 1:
                    # ngrams where 1 < n < window
                    ngram = prev_labels[:n]
                    self.add('ptagS-%s' % n, "#".join(ngram))
        # surronding contexts (left context = predicted tag, right context =
        # lexical info)
        lex_rhs_feats = self.feat_selection.get('lex_rhs', 0)
        rtags = self.lex_right_tags
        if lex_rhs_feats:
            if (len(prev_labels) >= 1) and (len(rtags) >= 1):
                self.add('lpred-rlex-surr', prev_labels[-1] + "#" + rtags[0])
        return

    def get_static_features(self):
        ''' features that can be computed independently from previous
        decisions'''
        self.get_word_features()
        self.get_conx_features()
        if self.lex_dict:
            self.add_lexicon_features()
        # NOTE: features for tag dict currently turned off
        # if self.tag_dict:
        #     self.add_tag_dict_features()
        return

    def get_word_features(self):
        ''' features computed based on word form: word form itself,
        prefix/suffix-es of length ln: 0 < n < ln, and certain regex
        patterns'''
        pln = self.feat_selection.get('pln', 4)  # 5
        sln = self.feat_selection.get('sln', 4)  # 5
        word = self.word
        index = self.index
        dico = self.lex_dict
        lex_tags = dico.get(word, {})
        # selecting the suffix confidence class for the word
        val = 1
        if len(lex_tags) == 1:
            val = list(lex_tags.values())[0]
        else:
            val = 1
            for v in list(lex_tags.values()):
                if v == "0":
                    val = 0
                    break
        # word string-based features
        if word in self.cache:
            # if wd has been seen, use cache
            self.add_cached_features(self.cache[word])
        else:
            # word string
            self.add('wd', word)
            # suffix/prefix
            wd_ln = len(word)
            if pln > 0:
                for i in range(1, pln + 1):
                    if wd_ln >= i:
                        self.add('pref%i' % i, word[:i])
            if sln > 0:
                for i in range(1, sln + 1):
                    if wd_ln >= i:
                        self.add('suff%i' % i, word[-i:], val)
        # regex-based features
        self.add('nb', number.search(word) is not None)
        self.add('hyph', hyphen.search(word) is not None)
#        self.add( 'eq', equals.search(word) != None )
        uc = upper.search(word)
        self.add('uc', uc is not None)
        self.add('niuc', uc is not None and index > 0)
        self.add('auc', allcaps.match(word) is not None)
        return

    def get_conx_features(self):
        ''' ngrams word forms in left and right contexts '''
        rpln = self.feat_selection.get('rpln', 1)
        rsln = self.feat_selection.get('rsln', 1)
        win = self.context_window
        lwds = self.left_wds
        rwds = self.right_wds
        # left/right contexts: ONLY UNIGRAMS FOR NOW
        for n in range(1, win + 1):
            # LHS
            if len(lwds) >= n:
                # unigram
                if n == 1:
                    left_unigram = lwds[-n]
                else:
                    left_unigram = lwds[-n:-n + 1][0]
                self.add('wd-%s' % n, left_unigram)
                # ngram
                # if n > 1:
                #    left_ngram = lwds[-n:]
                #    self.add('wdS-%s' %n, "#".join(left_ngram))
            # RHS
            if len(rwds) >= n:
                # unigram
                right_unigram = rwds[n - 1:n][0]
                self.add('wd+%s' % n, right_unigram)
                if n == 1:
                    # adding light suffix information for the right context
                    wd_ln = len(right_unigram)
                    #                    print >> sys.stderr, "right_unigram = %s (wd_ln = %i)" %(right_unigram,wd_ln)
                    #                    print >> sys.stderr, "  rsln = %i" %(rsln)
                    if rpln > 0:
                        for i in range(1, rpln + 1):
                            if wd_ln >= i:
                                self.add('pref+1-%i' % i, right_unigram[:i])
                    if rsln > 0:
                        for i in range(1, rsln + 1):
                            if wd_ln >= i:
                                self.add('suff+1-%i' % i, right_unigram[-i:])
                # ngram
                # if n > 1:
                #    right_ngram = rwds[:n]
                #    self.add('wdS+%s' %n, "#".join(right_ngram))
        # surronding contexts
        if win % 2 == 0:
            win // 2
            for n in range(1, win + 1):
                surr_ngram = lwds[-n:] + rwds[:n]
                if len(surr_ngram) == 2 * n:
                    self.add('surr_wds-%s' % n, "#".join(surr_ngram))

        return

    def _add_lex_features(self, dico, ltags, rtags, feat_suffix):  # for lex name
        lex_wd_feats = self.feat_selection.get('lex_wd', 0)
        lex_lhs_feats = self.feat_selection.get('lex_lhs', 0)
        lex_rhs_feats = self.feat_selection.get('lex_rhs', 0)
        if lex_wd_feats:
            # ------------------------------------------------------------
            # current word
            # ------------------------------------------------------------
            word = self.word
            uc = upper.search(word)
            lex_tags = dico.get(word, {})
            if not lex_tags and self.index == 0:
                # try lc'ed version for sent initial words
                lex_tags = dico.get(word.lower(), {})
            if len(lex_tags) == 0:
                self.add('%s' % feat_suffix, "unk")
            elif len(lex_tags) == 1:
                # unique tag
                t = list(lex_tags.keys())[0]
                self.add('%s-u' % feat_suffix, t, lex_tags[t])
            else:
                # disjunctive tag
                self.add('%s-disj' % feat_suffix, "|".join(lex_tags))
                # individual tags in disjunction
                for t in lex_tags:
                    self.add('%s-in' % feat_suffix, t)
                    # ?                   f = u'%s=%s:%s' %(feat_suffix,t,lex_tags[t])
            if uc is not None:
                uc_lex_tags = dico.get(word.lower(), {})
                if len(uc_lex_tags) == 0:
                    self.add('%s' % feat_suffix, "uc-unk")
                elif len(uc_lex_tags) == 1:
                    # unique tag
                    t = list(uc_lex_tags.keys())[0]
                    self.add('%s-uc-u' % feat_suffix, t, uc_lex_tags[t])
                else:
                    # disjunctive tag
                    self.add('%s-uc-disj' % feat_suffix, "|".join(uc_lex_tags))
                    # individual tags in disjunction
                    for t in uc_lex_tags:
                        self.add('%s-uc-in' % feat_suffix, t)
        # left and right contexts
        win = self.context_window
        for n in range(1, win + 1):
            # ------------------------------------------------------------
            # LHS -> lower results with those (understandable: predicted tag is a similar but less ambiguous source of info)
            # ------------------------------------------------------------
            # if lex_lhs_feats:
            #     if len(ltags) >= n:
            #         # unigram
            #         if n == 1:
            #             left_unigram = ltags[-n]
            #         else:
            #             left_unigram = ltags[-n:-n+1][0]
            #         self.add('%s-%s' %(feat_suffix,n), left_unigram)
            #         # ngram
            #         if n > 1:
            #             left_ngram = ltags[-n:]
            #             self.add('%sS-%s' %(feat_suffix,n), "#".join(left_ngram))
            # ------------------------------------------------------------
            # RHS
            # ------------------------------------------------------------
            if lex_rhs_feats:
                if len(rtags) >= n:
                    # unigram
                    right_unigram = rtags[n - 1:n][0]
                    self.add('%s+%s' % (feat_suffix, n), right_unigram)
                    # ngram
                    if n > 1:
                        right_ngram = rtags[:n]
                        self.add('%sS+%s' %
                                 (feat_suffix, n), "#".join(right_ngram))

        # surronding purely lexical contexts (left context = lexical info, not predicted tag)
        # if lex_lhs_feats and lex_rhs_feats:
        #     if win % 2 == 0:
        #         win /= 2
        #         for n in range(1,win+1):
        #             surr_ngram = ltags[-n:] + rtags[:n]
        #             if len(surr_ngram) == 2*n:
        # self.add('%s-surr-%s' %(feat_suffix,n), "#".join(surr_ngram))

        return

    def add_lexicon_features(self):
        lex = self.lex_dict
        l_tags = self.lex_left_tags
        r_tags = self.lex_right_tags
        self._add_lex_features(lex, l_tags, r_tags, feat_suffix='lex')
        return

    def add_tag_dict_features(self):
        lex = self.tag_dict
        l_tags = self.train_left_tags
        r_tags = self.train_right_tags
        self._add_lex_features(lex, l_tags, r_tags, feat_suffix='tdict')
        return
############################ utils.py ############################


def debug_n_best_sequence(n_best_sequences):
    print("debug")
    print(("\n".join(["%s/%.2f" % (" ".join([str(t) for t in l]), s)
                      for l, s in n_best_sequences])).encode("utf8"))
    print("----")


def word_list(file_path, t=5):
    word_ct = {}
    for s in BrownReader(file_path):
        for wd, tag in s:
            if tag != "__SPECIAL__":
                word_ct[wd] = word_ct.get(wd, 0) + 1
    filtered_wd_list = {}
    for w in word_ct:
        ct = word_ct[w]
        if ct >= t:
            filtered_wd_list[w] = ct
    return filtered_wd_list


def unserialize(filepath, encoding="utf-8"):
    _file = codecs.open(filepath, 'r', encoding=encoding)
    datastruct = loads(_file.read())
    _file.close()
    return datastruct
