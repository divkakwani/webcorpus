"""
Copyright © Divyanshu Kakwani 2019, all rights reserved.

Defines corpus reader, writer and processor
"""
import json
import os
import re
import sys
import subprocess

from tqdm import tqdm
from shutil import copyfile
from .utils import langcode2script, in_script, get_digits

# import bundled indic nlp library and resources

pkgdir = os.path.dirname(os.path.abspath(__file__))
indicnlp_lib_dir = os.path.join(pkgdir, 'vendor/indic_nlp_library')
indicnlp_resources_dir = os.path.join(pkgdir, 'vendor/indic_nlp_resources')

sys.path.append('{}/src'.format(indicnlp_lib_dir))

from indicnlp import common
from indicnlp import loader

common.set_resources_path(indicnlp_resources_dir)
loader.load()

from indicnlp.tokenize import indic_tokenize
from indicnlp.normalize import indic_normalize
from indicnlp.transliterate import unicode_transliterate
from indicnlp.tokenize import sentence_tokenize


class CorpusReader:

    def __init__(self, corpus_path, lang=None, fmt='json'):
        self.corpus_path = corpus_path
        self.lang = lang
        self.fmt = fmt

        self.files = []
        if os.path.isfile(corpus_path):
            self.files = [{'path': corpus_path}]
        else:
            for (dirpath, _, fnames) in os.walk(corpus_path):
                self.files += [{'publisher': os.path.basename(dirpath),
                                'path': os.path.join(dirpath, file)}
                               for file in fnames]

    def _get_content(self, fpath):
        if self.fmt != 'json':
            with open(fpath, 'r', encoding='utf-8', errors='replace') as fp:
                content = fp.read()
        else:
            # interpret as json
            with open(fpath, 'r', encoding='utf-8', errors='replace') as fp:
                try:
                    art = json.load(fp)
                    return art['content']
                except json.decoder.JSONDecodeError:
                    return None
        return content

    def sents(self):
        for fid in range(len(self.files)):
            content = self._get_content(self.files[fid]['path'])
            if content:
                sents = sentence_tokenize.sentence_split(content, self.lang)
                for sent in sents:
                    yield sent

    def articles(self):
        for fid in range(len(self.files)):
            fpath = self.files[fid]['path']
            with open(fpath) as fp:
                try:
                    art = json.load(fp)
                    art['publisher'] = self.files[fid]['publisher']
                    yield art
                except json.decoder.JSONDecodeError:
                    pass


class CorpusWriter:

    def __init__(self, corpus_path, amalgamated=True):
        self.corpus_path = corpus_path
        if amalgamated:
            self.fp = open(self.corpus_path, 'w', encoding='utf-8',
                           buffering=8192)
        else:
            os.makedirs(corpus_path, exist_ok=True)

    def add_sents(self, sents):
        if len(sents) <= 0:
            return

        sents = [sents] if isinstance(sents, str) else sents
        self.fp.write('\n'.join(sents))
        self.fp.write('\n')

    def add_article(self, art):
        publisher = art['publisher']
        del art['publisher']
        fpath = os.path.join(self.corpus_path, publisher, art['name'])
        os.makedirs(os.path.join(self.corpus_path, publisher), exist_ok=True)
        with open(fpath, 'w') as fp:
            json.dump(art, fp)


class CorpusProcessor:
    """
    Applies the following pre-processing steps. Read docs/data-processing.md
    for more details.
        * Remove sentences that contain one or more words not in the
          desired language
        * Remove short sentences
        * Treat punctuation marks as words. Insert spaces around them
        * Lowercase all the letters (in case of English)
        * Replace every number by # token
        * Remove "stop sentences"
    """

    def __init__(self, ip_corpus_path, lang, corpus_fmt, op_corpus_path):
        self.lang = lang
        self.script = langcode2script(lang)
        self.corpus_path = ip_corpus_path
        self.corpus_reader = CorpusReader(ip_corpus_path, lang, corpus_fmt)
        normalizer_factory = indic_normalize.IndicNormalizerFactory()
        self.normalizer = normalizer_factory.get_normalizer(lang)
        # self.stop_sents = self._stop_sents()
        self.stop_sents = set()
        self.corpus_writer = CorpusWriter(op_corpus_path)

    def _stop_sents(self):
        """
        All the seen sentences are maintained in the freq and first occurence
        dictionaries. The frequency counts are updated after seeing each
        sentence. As soon as the occurence rate of a sentence drops below
        `min_occur_rate`, it is removed from the freq dictionary.
        """
        freq, first_occur = {}, {}
        min_occur_rate, sno = 0.1, 0

        for sent in tqdm(self.corpus_reader.sents()):
            sno += 1
            sent = self._process_sent(sent)
            freq[sent] = freq.get(sent, 0) + 1
            first_occur[sent] = first_occur.get(sent, sno)
            # remove sentences with occurence rate less than min_occur_rate
            for sent in freq.copy():
                if (freq[sent] / (sno-first_occur[sent]+1)) < min_occur_rate:
                    del freq[sent], first_occur[sent]
        for sent in freq.copy():
            if (freq[sent] / sno) < min_occur_rate:
                del freq[sent], first_occur[sent]
        return freq.keys()

    def _process_sent(self, sent):
        newline_removed = sent.replace('\n', ' ')
        normalized = self.normalizer.normalize(newline_removed)
        num_masked = re.sub(r'[0-9]+', '#', normalized)
        native_digits = get_digits(self.script)
        num_masked = re.sub(r'[{}]+'.format(native_digits), '#', num_masked)
        spaced = ' '.join(indic_tokenize.trivial_tokenize(num_masked,
                                                          self.lang))
        return spaced

    def process(self):
        for sent in tqdm(self.corpus_reader.sents()):
            sent = self._process_sent(sent)
            if self._sent_filter(sent):
                self.corpus_writer.add_sents(sent)

    def _sent_filter(self, sent):
        if len(sent) < 10:
            return False
        for c in sent:
            if not in_script(c, self.script):
                return False
        return True
