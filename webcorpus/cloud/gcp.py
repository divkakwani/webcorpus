"""
Copyright © Divyanshu Kakwani 2020, all rights reserved

Interface to the cloud storage. It internally manages compression
and decompression of files. It also maintains statistics of the
files in firestore
"""
import os
import tarfile

from google.cloud import storage
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
        self.fsclient = firestore.client()

        self.client = storage.Client\
                             .from_service_account_json(self.bucketstore_key)
        self.bucket = self.client.get_bucket(self.bucket_name)

    def _push(self, remote_path, filename):
        blob = self.bucket.blob(remote_path)
        blob.upload_from_filename(filename=filename)

    def download(self, remote_path, download_path):
        blobs = self.client.list_blobs(
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
            os.makedirs(ufname)
            tar.extractall(path=ufname)

    def upload_stats(self, corpus, form):
        stats = corpus.get_stats()
        doc_ref = self.fsclient.collection('datasets').document(corpus.lang)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.update({'html.{}'.format(os.path.basename(corpus.path)): stats['num_files']})
        else:
            doc_ref.set({self.dtype: stats})

    def upload(self, corpus, form):
        path = corpus.archive()
        root_path = os.path.join('indicnlp-crawls', corpus.lang, form)
        blob_path = os.path.join(root_path, os.path.basename(path))
        self._push(blob_path, path)
        self.upload_stats(corpus, form)
        os.remove(path)
