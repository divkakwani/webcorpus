
import sys
import json

from webcorpus.corpus.io import CatCorpus
from hashlib import sha1


ic = CatCorpus(sys.argv[1])
oc = CatCorpus(sys.argv[2])

for cat, fname, data in ic.files():
    art = json.loads(data)
    tart = {'title': None, 'body': art['content'],
            'source': cat, 'url': art['source'],
            'timestamp': sys.argv[3]}
    iden = sha1(art['source'].encode('utf-8')).hexdigest()
    oc.add_file(cat, iden, json.dumps(tart, ensure_ascii=False))
