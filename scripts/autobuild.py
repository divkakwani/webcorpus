
import os
import shutil
import time

from google.cloud import storage
from webcorpus.processors.arts import ArtsProcessor
from webcorpus.processors.sent import SentProcessor
from webcorpus.corpus import SentCorpus
from firebase_admin import credentials, firestore, initialize_app


class Firestore:

    def __init__(self):
        # Initialize Firestore DB
        cred = credentials.Certificate('keys/firebase-key.json')
        self.default_app = initialize_app(cred)
        self.db = firestore.client()


class GCP:

    def __init__(self):
        self.client = storage.Client\
                      .from_service_account_json('keys/ai4b-gcp-key.json')
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

langs = ['or', 'as']


def get_blob_path(lang, dtype, source):
    return os.path.join('indicnlp-crawls', lang, dtype, source + '.tar.xz')


def get_job_list():
    job_list = []
    for lang in langs:
        doc_ref = fsclient.db.collection('datasets').document(lang)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()

            data['html'] = data.get('html', {})
            data['arts'] = data.get('arts', {})
            data['sent'] = data.get('sent', {})

            # arts jobs
            sources = list(data['html'].keys() - data['arts'].keys())
            job_list += list(zip([lang]*len(sources), sources,
                                 [True]*len(sources)))

            sources = list(data['arts'].keys() - data['sent'].keys())
            job_list += list(zip([lang]*len(sources), sources,
                                 [False]*len(sources)))
    return job_list


def run_jobs(job_list):
    for job in job_list:
        try:
            doc_ref = fsclient.db.collection('datasets').document(job[0])
            if job[2]:
                print('Building article for source: ' + job[1])
                gcp.pull(get_blob_path(job[0], 'html', job[1]),
                         '/tmp/{}_html.tar.xz'.format(job[1]))
                shutil.unpack_archive('/tmp/{}_html.tar.xz'.format(job[1]),
                                      '/tmp/{}'.format(job[1]), 'xztar')
                proc = ArtsProcessor(job[0], '/tmp/{}'.format(job[1]),
                                     '/tmp/{}_arts'.format(job[1]))
                proc.gen_dataset()
                shutil.rmtree('/tmp/{}'.format(job[1]))
                os.remove('/tmp/{}_html.tar.xz'.format(job[1]))
                shutil.make_archive('/tmp/{}_arts'.format(job[1]), 'xztar',
                                    '/tmp/{}_arts/{}'.format(job[1], job[1]))
                gcp.push(get_blob_path(job[0], 'arts', job[1]),
                         '/tmp/{}_arts.tar.xz'.format(job[1]))

                num_arts = len(os.listdir('/tmp/{0}_arts/{0}'.format(job[1])))
                doc_ref.update({'arts.{}'.format(job[1]): num_arts})
            else:
                gcp.pull(get_blob_path(job[0], 'arts', job[1]),
                         '/tmp/{}_arts.tar.xz'.format(job[1]))
                shutil.unpack_archive('/tmp/{}_arts.tar.xz'.format(job[1]),
                                      '/tmp/{}_arts'.format(job[1]), 'xztar')

            print('Building sent for source: ' + job[1])
            if os.path.exists('/tmp/{}_sent'.format(job[1])):
                os.remove('/tmp/{}_sent'.format(job[1]))
            proc = SentProcessor(job[0], '/tmp/{}_arts'.format(job[1]),
                                 '/tmp/{}_sent'.format(job[1]))
            proc.gen_dataset()
            shutil.make_archive('/tmp/{}_sent'.format(job[1]), 'xztar', '/tmp',
                                '{}_sent'.format(job[1]))
            gcp.push(get_blob_path(job[0], 'sent', job[1]),
                     '/tmp/{}_sent.tar.xz'.format(job[1]))

            corpus = SentCorpus('/tmp/{}_sent'.format(job[1]))
            doc_ref.update({'sent.{}'.format(job[1]): corpus.get_stats()['tokens']})
            os.remove('/tmp/{}_sent'.format(job[1]))
            os.remove('/tmp/{}_sent.tar.xz'.format(job[1]))
            os.remove('/tmp/{}_arts.tar.xz'.format(job[1]))
            shutil.rmtree('/tmp/{}_arts'.format(job[1]))
        except:
            pass


job_list = get_job_list()
run_jobs(job_list)
