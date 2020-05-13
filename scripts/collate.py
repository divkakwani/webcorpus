
import os
import shutil
import time
import tarfile
import urllib.request
import subprocess

from google.cloud import storage
from webcorpus.processors.arts import ArtsProcessor
from webcorpus.processors.sent import SentProcessor
from webcorpus.corpus.io import SentCorpus
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

    def pull(self, blob_path, file_path):
        blob = storage.Blob(blob_path, self.bucket)
        with open(file_path, 'wb') as file_obj:
            self.client.download_blob_to_file(blob, file_obj)

    def push(self, remote_path, filename):
        blob = self.bucket.blob(remote_path)
        blob.upload_from_filename(filename=filename)


gcp = GCP()
fsclient = Firestore()

# fetch the dataset from firestore
# based on it build a job list
# run the job

# each job is represented as (lang, source, compute_arts=False)

lang = 'kn' 


def get_blob_path(lang, dtype, source):
    return os.path.join('indicnlp-crawls', lang, dtype, source + '.tar.xz')


def dump_stats(lang, fname):
    subprocess.call('echo ' + lang + '  ' + fname + ' >> ../stats', shell=True)
    subprocess.call('wc -l < ' + fname + '  >> ../stats', shell=True)
    subprocess.call('cat ' + fname + ' | tr " " "\\n" | wc -l  >> ../stats', shell=True)
    subprocess.call('cat ' + fname + ' | tr " " "\\n" | runiq - | wc -l  >> ../stats', shell=True)


def process_lang(lang):
    os.makedirs(lang, exist_ok=True)
    os.chdir(lang)

    blobs = gcp.bucket.list_blobs(prefix='indicnlp-crawls/{}/sent'.format(lang))  # Get list of files
    filenames = []
    for blob in blobs:
        filename = blob.name[blob.name.rfind('/')+1:]
        filenames.append(filename)
        blob.download_to_filename(filename)  # Download

    for filename in filenames:
        ufname = filename.replace('.tar.xz', '')
        tar = tarfile.open(filename, mode='r:xz')
        tar.extractall(path='.')

    # download oscar
    # urllib.request.urlretrieve('https://traces1.inria.fr/oscar/files/compressed-orig/{}.txt.gz'.format(lang), 'oscar.txt.gz')
    # subprocess.call('gunzip oscar.txt.gz', shell=True)

    # generate f1, f2, f3, f4
    subprocess.call('cat *_sent > wc', shell=True)
    subprocess.call('runiq wc > wc_dedup', shell=True)
    # subprocess.call('cat wc oscar.txt > wc_cc', shell=True)
    # subprocess.call('runiq wc_cc > wc_cc_dedup', shell=True)

    dump_stats(lang, 'wc')
    dump_stats(lang, 'wc_dedup')
    # dump_stats(lang, 'wc_cc')
    # dump_stats(lang, 'wc_cc_dedup')

    shutil.make_archive('wc', 'xztar', '.', 'wc')
    shutil.make_archive('wc_dedup', 'xztar', '.', 'wc_dedup')
    # shutil.make_archive('wc_cc', 'xztar', '.', 'wc_cc')
    # shutil.make_archive('wc_cc_dedup', 'xztar', '.', 'wc_cc_dedup')

    gcp.push('indicnlp-datasets/monoling/{}/wc.tar.xz'.format(lang),  'wc.tar.xz')
    gcp.push('indicnlp-datasets/monoling/{}/wc_dedup.tar.xz'.format(lang),  'wc_dedup.tar.xz')
    # gcp.push('indicnlp-datasets/monoling/{}/wc_cc.tar.xz'.format(lang),  'wc_cc.tar.xz')
    # gcp.push('indicnlp-datasets/monoling/{}/wc_cc_dedup.tar.xz'.format(lang),  'wc_cc_dedup.tar.xz')

    os.chdir('..')
    shutil.rmtree(lang)


langs = ['en']

for lang in langs:
    print('processing', lang)
    process_lang(lang)
