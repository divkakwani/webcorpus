"""
Copyright © Divyanshu Kakwani 2020, all rights reserved

"""

import inspect
import os
from hashlib import sha1
from types import FunctionType

from .storage import Storage
from .archiver import Archiver


class SentCorpus:

    def __init__(self, lang, path):
        self.lang = lang
        self.root_path = path
        self.storage = Storage(self, mode='same', format='plain')
        self.archiver = Archiver(self)

    def __getattr__(self, attrname):
        if attrname in dir(self):
            return getattr(self, attrname)
        elif attrname in dir(self.storage):
            return getattr(self.storage, attrname)
        else:
            return getattr(self.archiver, attrname)


class NewsCorpus:

    def __init__(self, lang, path):
        self.lang = lang
        self.root_path = path
        self.storage = Storage(self, mode='distinct', format='csv')
        self.archiver = Archiver(self)

    def get_path(self, instance):
        iden = instance['url']
        source = instance['source']
        fname = sha1(iden.encode('utf-8')).hexdigest()
        return os.path.join(source, fname)

    def __getattr__(self, attrname):
        if attrname in dir(self):
            return getattr(self, attrname)
        elif attrname in dir(self.storage):
            return getattr(self.storage, attrname)
        else:
            return getattr(self.archiver, attrname)
