"""
Copyright © Divyanshu Kakwani 2019, all rights reserved.

This file defines corpus functions/classes - reader, writer, processor etc.

"""
import json
import os
import re
import sys
import subprocess

from tqdm import tqdm
from utils import langcode2script, in_script


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


class CorpusReader:

    def __init__(self, corpus_path, lang, fmt='json'):
        self.corpus_path, self.lang, self.fmt = corpus_path, lang, fmt
        self.fpaths, self.fid = [], 0
        if os.path.isfile(corpus_path):
            self.fpaths = [corpus_path]
        else:
            for (dir_path, _, fnames) in os.walk(corpus_path):
                self.fpaths += [os.path.join(dir_path, file)
                                for file in fnames]

    def _get_content(self, fpath):
        if self.fmt != 'json':
            with open(fpath) as fp:
                content = fp.read()
        else:
            # interpret as json
            with open(fpath) as fp:
                try:
                    art = json.load(fp)
                    return art['content']
                except json.decoder.JSONDecodeError:
                    return None
        return content

    def sents(self):
        while self.fid < len(self.fpaths):
            content = self._get_content(self.fpaths[self.fid])
            if content:
                sents = sentence_tokenize.sentence_split(content, self.lang)
                for sent in sents:
                    yield sent
            self.fid += 1

    def reset(self):
        self.fid = 0


class CorpusWriter:

    def __init__(self, corpus_path, amalgamated=True):
        self.corpus_path = corpus_path
        self.fp = open(self.corpus_path, 'w', encoding='utf-8', buffering=8192)

    def add_sents(self, sents):
        if len(sents) <= 0:
            return

        sents = [sents] if isinstance(sents, str) else sents
        self.fp.write('\n'.join(sents))
        self.fp.write('\n')


class CorpusProcessor:
    """
    Applies the following pre-processing steps. Read docs/data-processing.md
    for more details.
        * Remove sentences that contain one or more words not in the
          desired language
        * Treat punctuation marks as words. Insert spaces around them
        * Lowercase all the letters (in case of English)
        * Replace every number by # token
        * Remove "stop sentences"
    """

    def __init__(self, corpus_path, lang, corpus_fmt):
        self.lang = lang
        self.script = langcode2script(lang)
        self.corpus_path = corpus_path
        self.corpus_reader = CorpusReader(corpus_path, lang, corpus_fmt)
        normalizer_factory = indic_normalize.IndicNormalizerFactory()
        self.normalizer = normalizer_factory.get_normalizer(lang)
        # self.stop_sents = self._stop_sents()
        self.stop_sents = set()
        self.corpus_reader.reset()
        self.corpus_writer = CorpusWriter('./data/processed/' + self.lang)

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


class CorpusMetadataManager:

    def __init__(self):
        self._persist_fname = './data/datasets.json'
        try:
            self._persist_fp = open(self._persist_fname, 'r')
            self._pmetadata = json.load(self._persist_fp)
        except FileNotFoundError:
            self._pmetadata = {}

    def set_remote_link(self, corpus_path, link):
        self._update_metadata({'path': corpus_path, 'link': link})
        return

    def _update_metadata(self, metadata):
        dataset_id = metadata['path']
        if dataset_id not in self._pmetadata:
            self._pmetadata[dataset_id] = metadata
        else:
            self._pmetadata[dataset_id].update(metadata)
        with open(self._persist_fname, 'w') as fp:
            json.dump(self._pmetadata, fp, indent=4, sort_keys=True)

    def compute_stats(self, corpus_path):
        # if corpus_path in self._pmetadata:
        #     return self._pmetadata[corpus_path]
        if os.path.isdir(corpus_path):
            stats = self._stats_raw(corpus_path)
        else:
            stats = self._stats_processed(corpus_path)
        self._update_metadata(stats)
        return stats

    def _stats_raw(self, corpus_path):
        num_articles = sum(len(files) for r, d, files in os.walk(corpus_path))
        stats = {'path': corpus_path, 'num_articles': num_articles}
        return stats

    def _stats_processed(self, corpus_path):
        stats = {'path': corpus_path}
        try:
            cmd = 'cat {} | wc -l'.format(corpus_path)
            num_lines = subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                                shell=True)
            print(num_lines)
            cmd = 'cat {} | sort | uniq | wc -l'.format(corpus_path)
            num_ulines = subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                                 shell=True)
            print(num_ulines)
            cmd = 'cat {} | tr \' \' \'\n\' | wc -l'.format(corpus_path)
            num_toks = subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                               shell=True)
            print(num_toks)
            cmd = 'cat {} | tr \' \' \'\n\' | sort | uniq | wc -l'\
                .format(corpus_path)
            num_utoks = subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                                shell=True)
            stats['num_lines'] = int(num_lines)
            stats['num_unique_lines'] = int(num_ulines)
            stats['num_tokens'] = int(num_toks)
            stats['num_unique_tokens'] = int(num_utoks)
        except subprocess.CalledProcessError:
            pass
        return stats
