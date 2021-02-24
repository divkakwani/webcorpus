# Utility to compress/decompress data for storage on GCP

import sys
import shutil

op = sys.argv[1]
dirname = sys.argv[2]


if op == 'compress':
    for d in os.listdir(dirname):
        compressed_path = os.path.join(dirname, '_compressed')
        os.mkdir(compressed_path)
        shutil.make_archive(os.path.join(compressed_path, d), 'xztar', os.path.join(dirname, d))
else op == 'decompress':
    for arc in os.listdir(dirname):
        uncompressed_path = os.path.join(dirname, '_compressed')
        os.mkdir(uncompressed_path)
        shutil.unpack_archive(os.path.join(dirname, arc), uncompressed_path, 'xztar')

