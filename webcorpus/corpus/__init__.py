"""
Copyright © Divyanshu Kakwani 2020, all rights reserved

"""

import inspect
import os
import csv
import io
import json
from hashlib import sha1
from types import FunctionType


class JsonEncoder:

    def encode(self, obj):
        return json.dumps(obj, ensure_ascii=False, indent=4)

    def decode(self, txt):
        return json.loads(txt)


class PlainEncoder:

    def encode(self, obj):
        return str(obj)

    def decode(self, txt):
        return txt


class CsvEncoder:

    def encode(self, obj):
        output = io.StringIO()
        data = list(obj)
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(data)
        return output.getvalue()

    def decode(self, txt):
        reader = csv.reader([txt])
        return list(reader)[0] 


def get_encoder(scheme):
    if scheme == 'plain':
        return PlainEncoder()
    elif scheme == 'json':
        return JsonEncoder()
    elif scheme == 'csv':
        return CsvEncoder()


class FileCorpus:

    def __init__(self, lang, path, encoding='plain', sep='\n', header=False):
        self.lang = lang
        self.root_path = path
        self.sep = sep
        self.write_fp = open(self.root_path, 'a', encoding='utf-8', buffering=8192)
        self.encoder = get_encoder(encoding)

        if header:
            next(self.write_fp)

    def all_instances(self):
        with open(self.root_path, 'r', encoding='utf-8') as fp:
            for line in fp.readlines():
                yield line.rstrip('\n')

    def add_instance(self, obj):
        txt = self.encoder.encode(obj)
        self.write_fp.write(txt)
        self.write_fp.write(self.sep)

    def flush(self):
        self.write_fp.flush()


class DirCorpus:

    def __init__(self, lang, path, encoding='json'):
        self.lang = lang
        self.root_path = path
        self.encoder = get_encoder(encoding)

    def get_path(self, instance):
        """
        Need to specify if writing to the corpus
        """
        raise NotImplementedError

    def all_instances(self):
        for (dirpath, _, fnames) in os.walk(self.root_path):
            for fname in fnames:
                fpath = os.path.join(dirpath, fname)
                try:
                    with open(fpath, encoding='utf-8') as fp:
                        yield self.encoder.decode(fp.read())
                except:
                    pass

    def add_instance(self, instance):
        relpath = self.get_path(instance)
        abspath = os.path.join(self.root_path, relpath)
        os.makedirs(os.path.dirname(abspath), exist_ok=True)
        with open(abspath, 'w', encoding='utf-8') as fp:
            fp.write(self.encoder.encode(instance))


class NewsCorpus(DirCorpus):

    def get_path(self, instance):
        url = instance['url']
        source = instance['source']
        fname = sha1(url.encode('utf-8')).hexdigest()
        return os.path.join(source, fname)
