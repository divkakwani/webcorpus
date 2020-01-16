"""
Copyright © Divyanshu Kakwani 2019, all rights reserved

This file defines corpus io classes
"""

import os

from hashlib import sha1


class CatCorpus:
    """
    Categorical Corpus is a set of the triple (identifier, data, category)
    """

    def __init__(self, corpus_path):
        self.corpus_path = corpus_path

    def size(self):
        return len(os.walk(self.corpus_path))

    def files(self):
        for (dirpath, _, fnames) in os.walk(self.corpus_path):
            cat = os.path.basename(dirpath)
            for fname in fnames:
                fpath = os.path.join(dirpath, fname)
                with open(fpath, encoding='utf-8') as fp:
                    yield (cat, fname, fp.read())

    def add_file(self, cat, iden, data):
        fname = sha1(iden.encode('utf-8')).hexdigest()
        os.makedirs(os.path.join(self.corpus_path, cat), exist_ok=True)
        fpath = os.path.join(self.corpus_path, cat, fname)

        with open(fpath, 'w', encoding='utf-8') as fp:
            fp.write(data)


class SentCorpus:
    """
    Sentence corpus is a single file corpus. Reads and writes happen
    line by line
    """

    def __init__(self, corpus_path):
        self.corpus_path = corpus_path
        self.write_fp = open(self.corpus_path, 'w', encoding='utf-8',
                             buffering=8192)

    def sents(self):
        with open(self.corpus_path) as fp:
            for line in fp:
                yield line

    def add_sents(self, sents):
        if len(sents) <= 0:
            return
        sents = [sents] if isinstance(sents, str) else sents
        self.write_fp.write('\n'.join(sents))
        self.write_fp.write('\n')
