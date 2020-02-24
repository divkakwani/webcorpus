
import requests

from bs4 import BeautifulSoup
from webcorpus.sources import Sources
from webcorpus.utils import extract_domain

lang_tags = [('kn', 'kannada'), ('or', 'oriya'), ('gu', 'gujarati'), ('mr', 'marathi'), ('pa', 'punjabi')]
max_pages = 20


def make_url(tag, pno):
    return 'https://www.indiblogger.in/tag/{}&p={}'.format(tag, pno)

sources = {lang: Sources(lang, '../sources/{}.csv'.format(lang)) for lang, _ in lang_tags}

for lang, tag in lang_tags:
    for pno in range(1, max_pages):
        url = make_url(tag, pno)
        try:
            cont = requests.get(url).content
            page = BeautifulSoup(cont)
            anchors = page.findAll('a', {'class': 'external-link'})
            for anchor in anchors:
                url = anchor.get('href')
                sources[lang].add(name=extract_domain(url), home_url=url, sitemap_url='')
        except:
            continue

