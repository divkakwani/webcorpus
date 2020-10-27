
import os
import sys

from webcorpus.cloud.gcp import CloudStore
from webcorpus.corpus import NewsCorpus


lang = sys.argv[1]
dpath = sys.argv[2]

store = CloudStore(bucketstore_key='keys/ai4b-gcp-key.json',
                   firestore_key='keys/firestore-key.json',
                   bucket_name='nlp-corpora--ai4bharat')

sources = os.listdir(dpath)

for s in sources:
    c = NewsCorpus(lang, s)
    store.upload(c, 'html')
