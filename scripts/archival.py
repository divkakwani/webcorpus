# Utility to compress/decompress data for storage on GCP

import sys
import shutil
import os

from pathlib import Path

op = sys.argv[1]
dirname = sys.argv[2]


if op == 'compress':
    compressed_path = os.path.join(Path(dirname).parent, Path(dirname).name + '_compressed')
    os.mkdir(compressed_path)
    for d in os.listdir(dirname):
        shutil.make_archive(base_name=os.path.join(compressed_path, d),
                            format='xztar',
                            root_dir=dirname,
                            base_dir=d)
elif op == 'decompress':
    uncompressed_path = Path(dirname).stem + '_uncompressed'
    os.mkdir(uncompressed_path)
    for arc in os.listdir(dirname):
        shutil.unpack_archive(os.path.join(dirname, arc), uncompressed_path, 'xztar')

