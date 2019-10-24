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
        pkgdir = os.path.dirname(os.path.abspath(__file__))
        self._fpath = os.path.join(pkgdir,
                                   'sources/{}.csv'.format(self.langcode))
        self._fields = ['id', 'name', 'language', 'home_url',
                        'sitemap_url', 'active']

        self._sources = {}
        self._id2name = {}
        self._next_id = 0

        if os.path.isfile(self._fpath):
            self._load_sources()
            self.init_writers()
        else:
            # create a new file and write the headers
            self.init_writers('w')
        
    def init_writers(self, mode='a', close=False):
        if close: self._write_fp.close()
        # initialize the csv writer
        self._write_fp = open(self._fpath, mode)
        self._writer = csv.writer(self._write_fp)
        if 'w' in mode:
            # Write header
            self._writer.writerow(self._fields)
            self._write_fp.flush()

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
            
    def disable_inactives(self, datadir, threshold):
        disk_path = os.path.join(datadir, 'raw', self.langcode)
        for src_name in self._sources:
            dir = os.path.join(disk_path, src_name)
            if not os.path.isdir(dir):
                # self._sources[src_name]['active'] = False
                continue
            num_files = len(os.listdir(dir))
            if num_files < threshold:
                print('In-active:\t%20s\t(total: %d)'%(src_name, num_files))
                self._sources[src_name]['active'] = False
            else:
                self._sources[src_name]['active'] = True
        
        self.rewrite_csv()
        return
    
    def rewrite_csv(self):
        self.init_writers('w', close=True)
        for src_name in self._sources:
            source = self._sources[src_name]
            row = list(map(lambda f: source[f], self._fields))
            self._writer.writerow(row)
        self._write_fp.flush()