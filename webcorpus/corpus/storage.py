"""
Copyright © Divyanshu Kakwani 2020, all rights reserved
"""

import os
import csv
import json


class Storage:
    """
    For simplification, assume that 
    if format = 'json', then mode = 'distinct'
    and if format = 'plain', then mode = 'same'
    """
    def __init__(self, corpus, mode=None, format=None, **options):
        self.mode = mode
        if mode == 'same':
            self.backend = SFStorage(corpus, options.get('sep', '\n'))
        elif mode == 'distinct':
            self.backend = MFStorage(corpus)

    def add_instance(self, instance):
        return self.backend.write(instance)

    def all_instances(self):
        return self.backend.read_all()

    def flush(self):
        if self.mode == 'same':
            self.backend.flush()
        

class SFStorage:

    def __init__(self, corpus, sep):
        self.corpus = corpus
        self.write_fp = open(corpus.root_path, 'a', encoding='utf-8', buffering=8192)
        self.sep = sep

    def write(self, txt):
        self.write_fp.write(txt)
        self.write_fp.write(self.sep)

    def read_all(self):
        with open(self.corpus.root_path, 'r', encoding='utf-8') as fp:
            for line in fp.readlines():
                yield line.rstrip('\n')

    def flush(self):
        self.write_fp.flush()


class MFStorage:

    def __init__(self, corpus):
        self.corpus = corpus

    def write(self, instance):
        relpath = self.corpus.get_path(instance)
        abspath = os.path.join(self.corpus.root_path, relpath)
        os.makedirs(os.path.dirname(abspath), exist_ok=True)
        with open(abspath, 'w', encoding='utf-8') as fp:
            json.dump(instance, fp, ensure_ascii=False, indent=4)

    def read_all(self):
        for (dirpath, _, fnames) in os.walk(self.corpus.root_path):
            for fname in fnames:
                fpath = os.path.join(dirpath, fname)
                try:
                    with open(fpath, encoding='utf-8') as fp:
                        yield (fpath, json.load(fp))
                except:
                    pass