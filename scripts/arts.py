
import os
import sys
from pathlib import Path

from webcorpus.processors.arts import ArtsProcessor
from webcorpus.processors.sent import SentProcessor



# lang = sys.argv[1]
# dirname = '/home/divkakwani/' + lang
# outdir = '/home/divkakwani/' + lang + '_arts'

# proc = ArtsProcessor(lang, dirname, outdir) 
proc = SentProcessor('as', '/home/divkakwani/as_old', '/home/divkakwani/as_sent') 
proc.gen_dataset()
