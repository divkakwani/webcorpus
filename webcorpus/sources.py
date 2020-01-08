"""
Copyright © Divyanshu Kakwani 2019, all rights reserved.
"""

import csv
import os


class Sources:
    """A set of news sources backed by a disk file

    In addition to iteration, it supports the following methods:
        get, add, update, delete
    """

    def __init__(self, lang, file_path):
        self.lang = lang
        self.fpath = file_path
        self.fields = ['name', 'home_url', 'sitemap_url', 'use_sitemap',
                       'active']
        self._sources = self._load() if os.path.isfile(self.fpath) else {}

    def __iter__(self):
        self.idx = 0
        self._sources_list = list(self._sources.values())
        return self

    def __next__(self):
        if self.idx >= len(self._sources_list):
            raise StopIteration
        source = self._sources_list[self.idx]
        self.idx += 1
        if not source['active']:
            return self.__next__()
        return source

    def _load(self):
        _sources = {}
        with open(self.fpath) as fp:
            reader = csv.DictReader(fp)
            for source in reader:
                source['active'] = (source['active'] == 'True')
                source['use_sitemap'] = (source['use_sitemap'] == 'True')
                source['lang'] = self.lang
                _sources[source['name']] = dict(source)
        return _sources

    def _write(self):
        with open(self.fpath, 'w', buffering=1) as fp:
            writer = csv.writer(fp)
            writer.writerow(self.fields)
            rows = [[self._sources[name][f] for f in self.fields]
                    for name in self._sources]
            rows = sorted(rows, key=lambda r: r[0])
            writer.writerows(rows)
            fp.flush()

    def all(self):
        return self._sources.copy()

    def get(self, name):
        return self._sources[name]

    def update(self, **kwargs):
        if len(set(kwargs) - set(self.fields)) != 0:
            raise 'Unknown fields'
        name = kwargs['name']
        self._sources[name].update(kwargs)
        self._write()

    def add(self, **kwargs):
        name = kwargs['name']

        if name in self._sources:
            return  # no-op

        kwargs['active'] = kwargs.get('active', True)
        kwargs['use_sitemap'] = kwargs.get('use_sitemap', False)
        if set(kwargs) != set(self.fields):
            raise 'Missing fields'

        self._sources[name] = kwargs
        self._write()
