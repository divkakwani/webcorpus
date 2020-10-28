
import os
import sys

from webcorpus.cloud.gcp import CloudStore
from webcorpus.corpus import NewsCorpus


lang = sys.argv[1]
dpath = sys.argv[2]

store = CloudStore(bucketstore_key='keys/ai4b-gcp-key.json',
                   firestore_key='keys/firebase-key.json',
                   bucket_name='nlp-corpora--ai4bharat')

sources = os.listdir(dpath)

for s in sources:
    path = os.path.join(dpath, s)
    c = NewsCorpus(lang, path)
    store.upload(c, 'html')
