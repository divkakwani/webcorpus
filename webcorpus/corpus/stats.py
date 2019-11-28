
import os
import subprocess


dirname = os.path.dirname(__file__)
script_path = os.path.join(dirname, 'stats.sh')


def print_stats(corpus_path):
    subprocess.call([script_path, corpus_path])
