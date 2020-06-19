"""
Copyright © Divyanshu Kakwani 2020, all rights reserved
"""

import os
import csv
import json


class BaseStorage:

    def __init__(self, **kwargs):
        self.root_path = kwargs['path']

    def _create_writer(self, filepath):
        fp = open(filepath, 'w', encoding='utf-8', buffering=8192)
        return fp

    def _write_payload(self, fp, payload):
        fp.write(payload)
        fp.write('\n')

    def load_instance(self, payload):
        """Unmarshall data instance"""
        return payload

    def dump_instance(self, instance):
        """Marshall data instance"""
        return instance

    def _write_instance(self, fp, instance):
        payload = self.dump_instance(instance)
        self._write_payload(fp, payload)

    def add_instance(self, instance):
        raise NotImplementedError

    def instances(self):
        raise NotImplementedError

    def get_filepaths(self):
        raise NotImplementedError


class SFStorage(BaseStorage):

    def __init__(self, **kwargs):
        self.fp = self._create_writer(kwargs['path'])
        BaseStorage.__init__(self, **kwargs)

    def add_instance(self, instance):
        self._write_instance(self.fp, instance)

    def instances(self):
        with open(self.root_path, 'r', encoding='utf-8') as fp:
            for line in fp.readlines():
                yield line.rstrip('\n')

    def get_filepaths(self):
        return [self.root_path]

    def flush(self):
        self.fp.flush()


class MFStorage(BaseStorage):

    def get_path(self, instance):
        print(dir(self))
        raise NotImplementedError

    def add_instance(self, instance):
        relpath = self.get_path(instance)
        abspath = os.path.join(self.root_path, relpath)
        os.makedirs(os.path.dirname(abspath), exist_ok=True)
        with self._create_writer(abspath) as fp:
            self._write_instance(fp, instance)

    def instances(self):
        for (dirpath, _, fnames) in os.walk(self.root_path):
            for fname in fnames:
                fpath = os.path.join(dirpath, fname)
                with open(fpath, encoding='utf-8') as fp:
                    yield (fpath, fp.read())

    def get_filepaths(self):
        filepaths = []
        for (dirpath, _, fnames) in os.walk(self.root_path):
            for fname in fnames:
                fpath = os.path.join(dirpath, fname)
                filepaths.append(fpath)
        return filepaths


class JsonStorage(BaseStorage):

    def _write_payload(self, fp, payload):
        json.dump(payload, fp)


class CsvStorage(BaseStorage):

    def _write_payload(self, fp, payload):
        writer = csv.writer(fp)
        writer.writerow(payload)

    def _create_writer(self, path):
        fp = open(path, 'w', encoding='utf-8', buffering=8192)
        writer = csv.writer(fp)
        writer.writerow(self.fields)
        return fp

    def set_header(self, fields):
        self.fields = fields
