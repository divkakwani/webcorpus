import random
import os
import sys

from webcorpus.sources import Sources
from firebase_admin import credentials, firestore, initialize_app


USAGE = 'dump-sources [srcdir]'

srcdir = sys.argv[1]

# Initialize Firestore DB
cred = credentials.Certificate('firebase-key.json')
default_app = initialize_app(cred)
db = firestore.client()

files = list(filter(lambda s: s.endswith('csv'), os.listdir(srcdir)))
langs = [os.path.splitext(f)[0] for f in files]

for lang, file in zip(langs, files):
    sources = list(Sources(lang, os.path.join(srcdir, file)))
    random.shuffle(sources)
    doc_ref = db.collection('sources').document(lang)
    doc_ref.set({source['name']: source for source in sources})
