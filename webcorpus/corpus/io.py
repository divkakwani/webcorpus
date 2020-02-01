"""
Copyright © Divyanshu Kakwani 2019, all rights reserved

This file define classes for the following two forms of dataset:

1. Categorical Corpus (CatCorpus)
2. Sentence Corpus (SentCorpus)

The classes provide i/o and statisitics operations

"""

import os
import subprocess
import itertools as it

from hashlib import sha1


def _exec_cmd(cmd):
    ret, out, errstr = 0, None, None
    cmd = '/bin/bash -o pipefail -c \'{}\''.format(cmd)
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                      shell=True)
    except subprocess.CalledProcessError as err:
        errstr = err.output
        ret = err.returncode
    return (ret, out, errstr)


class CatCorpus:
    """
    Categorical Corpus is a set of the triple (identifier, data, category)
    """

    def __init__(self, corpus_path):
        self.corpus_path = corpus_path

    def num_files(self):
        counts = {}
        cats = os.listdir(self.corpus_path)
        for cat in cats:
            cat_path = os.path.join(self.corpus_path, cat)
            count = len(os.listdir(cat_path))
            counts[cat] = count
        # total = sum(count for count in counts.values())
        # counts['total'] = total
        return counts

    def disk_size(self):
        cmd = 'du -s {} | cut -f1'.format(self.corpus_path)
        ret, out, errstr = _exec_cmd(cmd)
        if errstr:
            raise 'Error'
        return int(out)

    def stats(self):
        stat_dict = self.num_files()
        # stat_dict['disk_size'] = self.disk_size()
        return stat_dict

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
        self.write_fp = open(self.corpus_path, 'a', encoding='utf-8',
                             buffering=8192)

    def sents(self):
        with open(self.corpus_path) as fp:
            for line in fp:
                yield line

    def stats(self):
        cmd_lines = 'wc -l {} | cut -d" " -f1'.format(self.corpus_path)
        # cmd_uniqlines = 'awk "!($0 in a) {{a[$0];print}}" "{}" | wc -l'\
        #                 '| cut -f1'.format(self.corpus_path)
        cmd_tokens = 'tr " " "\n" < "{}" | wc -l | cut -f1'\
                     .format(self.corpus_path)
        # cmd_uniqtokens = 'tr " " "\n" < "{}" | awk "!($0 in a)'\
        #                  '{{a[$0];print}}" | wc -l | cut -f1'\
        #                  .format(self.corpus_path)

        _, lines, e1 = _exec_cmd(cmd_lines)
        # _, uniq_lines, e2 = _exec_cmd(cmd_uniqlines)
        _, tokens, e3 = _exec_cmd(cmd_tokens)
        # _, uniq_tokens, e4 = _exec_cmd(cmd_uniqtokens)

        return {
            'lines': int(lines),
            # 'uniq_lines': int(uniq_lines),
            'tokens': int(tokens)
            # 'uniq_tokens': int(uniq_tokens)
        }

    def add_sents(self, sents):
        if len(sents) <= 0:
            return
        sents = [sents] if isinstance(sents, str) else sents
        self.write_fp.write('\n'.join(sents))
        self.write_fp.write('\n')
