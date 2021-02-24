"""
Copyright © Divyanshu Kakwani 2020, all rights reserved
"""

import logging
import os
import tarfile


class Archiver:

    def __init__(self, corpus, **options):
        self.corpus = corpus

    def archive(self, path=None, method='xz'):
        basename = os.path.basename(self.corpus.root_path)
        basedir = os.path.dirname(self.corpus.root_path)
        if not path:
            path = os.path.join(basedir, basename + '.tar.xz')
        logging.info('Archiving {} to {}'.format(self.corpus.root_path, path))
        tar = tarfile.open(path, 'w:xz')
        tar.add(self.corpus.root_path, arcname=basename)
        tar.close()
        return path