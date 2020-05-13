"""
Copyright © Divyanshu Kakwani 2020, all rights reserved

Interface to the cloud storage. It internally manages compression
and decompression of files. It also maintains statistics of the
files in firestore
"""
import click
import shutil
import os
import tempfile

from google.cloud import storage
from ..corpus.io import CatCorpus, SentCorpus
from firebase_admin import credentials, firestore, initialize_app


class CloudStore:

    def __init__(self, *args, **kwargs):
        """
        Initialize fire store and bucket store clients
        """
        self.bucketstore_key = kwargs['bucketstore_key']
        self.firestore_key = kwargs['firestore_key']
        self.bucket_name = kwargs['bucket_name']
        
        # Initialize Firestore DB
        cred = credentials.Certificate(self.firestore_key)
        self.default_app = initialize_app(cred)
        self.db = firestore.client()

        self.client = storage.Client\
                      .from_service_account_json(self.bucketstore_key)
        self.bucket = self.client.get_bucket(self.bucket_name)

    def _push(self, remote_path, filename):
        blob = self.bucket.blob(remote_path)
        blob.upload_from_filename(filename=filename)

    def download(self, remote_path, download_path):
        blobs = storage_client.list_blobs(
            self.bucket_name, prefix=remote_path, delimiter=None
        )
        filenames = []
        for blob in blobs:
            filename = blob.name[blob.name.rfind('/')+1:]
            filename = os.path.join(download_path, filename)
            filenames.append(filename)
            blob.download_to_filename(filename)

        for filename in filenames:
            ufname = filename.replace('.tar.xz', '')
            tar = tarfile.open(filename, mode='r:xz')
            tar.extractall(path='.')

    def upload(self):
        pass


def tmpfile_path():
    tmp_name = next(tempfile._get_candidate_names())
    tmp_dir = tempfile._get_default_tempdir()
    return os.path.join(tmp_dir, tmp_name)


class CatCorpusHandler:

    def __init__(self, lang, path, dtype):
        self.corpus = CatCorpus(path)
        self.path = path
        self.lang = lang
        self.dtype = dtype

    def push_stats(self):
        stats = self.corpus.stats()
        doc_ref = fsclient.db.collection('datasets').document(self.lang)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.update({'{}.{}'.format(self.dtype, key): stats[key]
                            for key in stats})
        else:
            doc_ref.set({self.dtype: stats})

    def push(self, root_path):
        cats = os.listdir(self.path)
        for cat in cats:
            cat_path = os.path.join(self.path, cat)
            tmp_path = tmpfile_path()
            print('Archiving {} to {}'.format(cat_path, tmp_path))
            shutil.make_archive(tmp_path, 'xztar', cat_path)
            blob_path = os.path.join(root_path, cat + '.tar.xz')
            gcp.push(blob_path, tmp_path + '.tar.xz')


class SentCorpusHandler:

    def __init__(self, lang, path, dtype, source):
        self.corpus = SentCorpus(path)
        self.path = path
        self.lang = lang
        self.source = source

    def push_stats(self):
        stats = self.corpus.stats()
        doc_ref = fsclient.db.collections('datasets').document(self.lang)
        doc = doc_ref.get
        if doc.exists:
            doc_ref.update({'{}.{}'.format(self.dtype, key): stats[key]
                            for key in stats})
        else:
            doc_ref.set({self.dtype: stats})

    def push(self, root_path):
        tmp_path = tmpfile_path()
        print('Archiving {} to {}'.format(self.path, tmp_path))
        shutil.make_archive(tmp_path, 'xztar', self.path)
        blob_path = os.path.join(root_path, self.source + '.tar.xz')
        gcp.push(blob_path, tmp_path + '.tar.xz')


def make_root_path(lang, dtype):
    return os.path.join('indicnlp-crawls', lang, dtype)
