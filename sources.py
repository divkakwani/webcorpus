"""
Copyright © Divyanshu Kakwani 2019, all rights reserved.
"""

import csv
import os


class SourceList:
    """
    Represents a storage-persisted source list
    """

    def __init__(self, langcode):
        self.langcode = langcode
        self._fpath = 'data/sources/{}.csv'.format(self.langcode)
        self._fields = ['id', 'name', 'language', 'home_url',
                        'sitemap_url', 'active']

        self._sources = {}
        self._id2name = {}
        self._next_id = 0

        if os.path.isfile(self._fpath):
            self._load_sources()
        else:
            # create a new file and write the headers
            fp = open(self._fpath, 'w')
            writer = csv.writer(fp)
            writer.writerow(self._fields)
            fp.close()

        # initialize the csv writer
        self._write_fp = open(self._fpath, 'a')
        self._writer = csv.writer(self._write_fp)

    def _load_sources(self):
        fp = open(self._fpath)
        reader = csv.DictReader(fp)
        for source in reader:
            source['id'] = int(source['id'])
            source['active'] = (source['active'] == 'True')
            self._sources[source['name']] = dict(source)
            self._id2name[source['id']] = source['name']
            self._next_id = max(source['id']+1, self._next_id)
        fp.close()

    def __iter__(self):
        self.cid = 0
        return self

    def __next__(self):
        if self.cid < self._next_id:
            source = self._sources[self._id2name[self.cid]]
            self.cid += 1
            return source
        else:
            raise StopIteration

    def get_source(self, name):
        return self._sources[name]

    def add_source(self, source):
        assert(source['language'] == self.langcode)
        if source['name'] not in self._sources:
            source = source.copy()
            source['id'] = self._next_id
            source['active'] = True
            self._next_id += 1
            self._sources[source['name']] = source
            row = list(map(lambda f: source[f], self._fields))
            self._writer.writerow(row)
            self._write_fp.flush()
