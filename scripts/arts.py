
import os
import sys
from pathlib import Path

from webcorpus.processors.arts import ArtsProcessor



lang = sys.argv[1]
dirname = '/home/divkakwani/' + lang
outdir = '/home/divkakwani/' + lang + '_arts'

proc = ArtsProcessor(lang, dirname, outdir) 
proc.run()
