
import os
import sys

from webcorpus.processors.arts import ArtsProcessor



lang = sys.argv[1]
dirname = sys.argv[2]


proc = ArtsProcessor(lang, dirname, os.path.join(dirname, '_arts'))
proc.gen_dataset()
