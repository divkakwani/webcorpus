"""
Tricks in preparing dataset
============================

1. Remove punctuation marks
2. Remove frequently occuring sentences
3. Text Normalization
"""

import os
import re
import sys
import string


INDIC_NLP_LIB_HOME = './vendor/indic_nlp_library'
INDIC_NLP_RESOURCES = './vendor/indic_nlp_resources'

sys.path.append('{}/src'.format(INDIC_NLP_LIB_HOME))

from indicnlp import common
from indicnlp import loader

common.set_resources_path(INDIC_NLP_RESOURCES)
loader.load()

from indicnlp.tokenize import indic_tokenize
from indicnlp.normalize import indic_normalize
from indicnlp.transliterate import unicode_transliterate
from indicnlp.tokenize import sentence_tokenize


class NewsCorpusReader:

    def __init__(self, corpus_path):
        self.file_paths = []
        for (dpath, _, fnames) in os.walk(corpus_path):
            self.file_paths += [os.path.join(dpath, file) for file in fnames]
        self.file_idx = 0

    def read_articles(self):
        while self.file_idx < len(self.file_paths):
            article = open(self.file_paths[self.file_idx]).read()
            yield article
            self.file_idx += 1

    def reset(self):
        self.file_idx = 0


class NewsCorpusWriter:

    def __init__(self, corpus_path, amalgamated=True):
        self.corpus_path = corpus_path
        self.fp = open(self.corpus_path, 'w', encoding='utf-8')
        self.writing_started = False

    def add_article(self, sents):
        if len(sents) > 0 and self.writing_started:
            self.fp.write('\n')
        if not self.writing_started:
            self.writing_started = True
        self.fp.write('\n'.join(sents))


class NewsCorpusProcessor:

    def __init__(self, corpus_path, lang):
        self.lang = lang
        self.corpus_path = corpus_path
        self.corpus_reader = NewsCorpusReader(corpus_path)
        normalizer_factory = indic_normalize.IndicNormalizerFactory()
        self.normalizer = normalizer_factory.get_normalizer(lang)
        self.stop_sents = set(self._stop_sents())
        self.corpus_reader.reset()
        self.corpus_writer = NewsCorpusWriter('./data/processed/' + self.lang)
        print(self.stop_sents)

    def _stop_sents(self):
        """
        All the seen sentences are maintained in the freq dictionary. The
        frequency counts are updated after seeing each article. As soon as
        the occurence rate of a sentence drops below `min_occur_rate`, it
        is removed from the freq dictionary.
        """
        freq = {}
        min_occur_rate = 0.1
        total = 0
        for article in self.corpus_reader.read_articles():
            total += 1
            sents = sentence_tokenize.sentence_split(article, 'hi')
            sents = map(self._process_sent, sents)
            for sent in sents:
                freq[sent] = freq.get(sent, 0) + 1
            # remove sentences with occurence rate less than min_occur_rate
            for sent in freq.copy():
                if (freq[sent]/total) < min_occur_rate:
                    del freq[sent]
        return freq.keys()

    def _process_sent(self, sent):
        newline_removed = sent.replace('\n', ' ')
        normalized = self.normalizer.normalize(newline_removed)
        exclude = set(string.punctuation)
        punc_removed = ''.join(c for c in normalized if c not in exclude)
        return punc_removed

    def process(self):
        for article in self.corpus_reader.read_articles():
            sents = sentence_tokenize.sentence_split(article, 'hi')
            sents = map(self._process_sent, sents)
            sents = list(filter(self._sent_filter, sents))
            self.corpus_writer.add_article(sents)

    def _sent_filter(self, sent):
        if sent in self.stop_sents or len(sent) < 10:
            return False
        if re.search('[a-zA-Z]', sent) is not None:
            return False
        return True
