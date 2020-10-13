"""
Copyright © Divyanshu Kakwani 2020, all rights reserved

"""

import inspect
import os
from hashlib import sha1
from types import FunctionType

from .storage import SFStorage, MFStorage, JsonStorage, CsvStorage
from .stats import PlainCorpusStats
from .archiver import SFArchiver, MFArchiver


def get_fmt_class(fmt):
    if fmt == 'csv':
        return CsvStorage
    elif fmt == 'json':
        return JsonStorage
    else:
        return None


def get_store_class(store_in):
    if store_in == 'single':
        return SFStorage
    elif store_in == 'separate':
        return MFStorage


def get_storage_class(store_in, fmt):
    store_cls = get_stats_class(store_in)
    fmt_cls = get_fmt_class(fmt)
    name = store_cls.__name__ + '_' + fmt_cls.__name__
    return type(name, (fmt_cls, store_cls), dict(store_cls.__dict__))


def get_stats_class(fmt):
    if fmt == 'plain':
        return PlainCorpusStats
    else:
        return None


def get_archive_class(store_in):
    if store_in == 'single':
        return SFArchiver
    elif store_in == 'separate':
        return MFArchiver


class Mixinator(type):
    """
    Dynamicaly modify class with some extra mixins.
    """
    def __call__(cls, *args, **kwargs):
        if hasattr(cls, '_meta_args'):
            store_in = cls._meta_args.get('store_in')
            fmt = cls._meta_args.get('fmt')
        else:
            store_in = kwargs.get('store_in')
            fmt = kwargs.get('fmt')
        mixins = []
        mixins.append(get_fmt_class(fmt))
        mixins.append(get_store_class(store_in))
        mixins.append(get_stats_class(fmt))
        mixins.append(get_archive_class(store_in))
        mixins = tuple(filter(lambda t: t is not None, mixins))
        cls._mixins = mixins
        new_cls = type(cls.__name__, mixins + (cls,), dict(cls.__dict__))
        return super(Mixinator, new_cls).__call__(*args, **kwargs)


class BasicCorpus(metaclass=Mixinator):

    def __init__(self, *args, **kwargs):
        # initialize mixins
        kwargs['corpus'] = self
        self.lang = kwargs['lang']
        for mixin in self.__class__._mixins:
            mixin.__init__(self, *args, **kwargs)


class SentCorpus(BasicCorpus):

    _meta_args = {'store_in': 'single', 'fmt': 'plain'}

    def __init__(self, lang, path):
        BasicCorpus.__init__(self, lang=lang, path=path)

    def add_sent(self, sent):
        self.add_instance(sent)

    def sents(self):
        return self.instances()


class NewsCorpus(BasicCorpus):

    _meta_args = {'store_in': 'separate', 'fmt': 'json'}

    def __init__(self, lang, path):
        self.path = path
        BasicCorpus.__init__(self, lang=lang, path=path)

    def get_path(self, instance):
        iden = instance['url']
        fname = sha1(iden.encode('utf-8')).hexdigest()
        return fname
