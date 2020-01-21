"""
Script for querying GCP store

With this script, you can:
* compress and upload files on GCP in the correct format
* Download and uncompress files from GCP
* update metadata in firestore automatically with the upload operation

"""
import click
import shutil
import os
import tempfile

from google.cloud import storage
from webcorpus.corpus.io import CatCorpus, SentCorpus
from firebase_admin import credentials, firestore, initialize_app


class Firestore:

    def __init__(self):
        # Initialize Firestore DB
        cred = credentials.Certificate('firebase-key.json')
        self.default_app = initialize_app(cred)
        self.db = firestore.client()


class GCP:

    def __init__(self):
        self.client = storage.Client\
                      .from_service_account_json('ai4b-gcp-key.json')
        self.bucket = self.client.get_bucket('nlp-corpora--ai4bharat')

    def push(self, remote_path, filename):
        blob = self.bucket.blob(remote_path)
        blob.upload_from_filename(filename=filename)


gcp = GCP()
fsclient = Firestore()


def tmpfile_path():
    tmp_name = next(tempfile._get_candidate_names())
    tmp_dir = tempfile._get_default_tempdir()
    return os.path.join(tmp_dir, tmp_name)


class CatCorpusHandler:

    def __init__(self, lang, path, dtype):
        self.corpus = CatCorpus(path)
        self.path = path
        self.lang = lang

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
        cats = os.listdir(self.path)
        for cat in cats:
            cat_path = os.path.join(self.path, cat)
            tmp_path = tmpfile_path()
            print('Archiving {} to {}'.format(cat_path, tmp_path))
            shutil.make_archive(tmp_path, 'xztar', cat_path)
            blob_path = os.path.join(root_path, cat)
            gcp.push(blob_path, tmp_path + '.tar.xz')


class SentCorpusHandler:

    def __init__(self, lang, path, dtype):
        self.corpus = SentCorpus(path)

    def push_stats(self):
        pass

    def push(self):
        pass


def make_root_path(lang, dtype):
    return os.path.join('indicnlp-crawls', lang, dtype)


@click.group()
def cli():
    pass


@cli.command(name='upload')
@click.option('--lang', required=True)
@click.option('--path', required=True)
@click.option('--dtype', metavar='type',
              type=click.Choice(['arts', 'html', 'sent']), required=True)
def upload(lang, path, dtype):
    if dtype in ('arts', 'html'):
        handler = CatCorpusHandler(lang, path, dtype)
    elif dtype == 'sent':
        handler = SentCorpusHandler(lang, path, dtype)
    else:
        raise 'Invalid '

    # push stats to firestore
    handler.push_stats()

    # push to gcp
    root_path = make_root_path(lang, dtype)
    handler.push(root_path)


@cli.command(name='download')
@click.option('--lang', required=True)
@click.option('--path', required=True)
@click.option('--dtype', metavar='type',
              type=click.Choice(['arts', 'html', 'sent']), required=True)
def download(lang, path, dtype):
    pass


if __name__ == '__main__':
    cli()
