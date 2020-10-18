#!/usr/bin/env python3

import random
import os
import sys

from webcorpus.sources import Sources
from firebase_admin import credentials, firestore, initialize_app


if len(sys.argv) != 3:
    print('Usage: ./sync-sources.py <src-dir> <firestore-key-path>')
else:
    srcdir, key_path = sys.argv[1], sys.argv[2]


# Initialize Firestore DB
cred = credentials.Certificate(key_path)
default_app = initialize_app(cred)
db = firestore.client()

files = list(filter(lambda s: s.endswith('csv'), os.listdir(srcdir)))
langs = [os.path.splitext(f)[0] for f in files]

for lang, file in zip(langs, files):
    sources = list(Sources(lang, os.path.join(srcdir, file)))
    random.shuffle(sources)
    doc_ref = db.collection('sources').document(lang)
    doc_ref.set({source['name']: source for source in sources})
