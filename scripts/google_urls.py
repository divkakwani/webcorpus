
"""

"""

import re
import urllib
import requests
import pycld2 as cld2
import time

from urllib.parse import urlparse
from googlesearch import search
from webcorpus.language import LC_NAME


keywords = {
    'mr': ['marathi news', 'marathi tv', 'marathi magazine'],
    'pa': ['punjabi news', 'punjabi tv', 'punjabi magazine'],
    'gu': ['gujarati news', 'gujarati tv', 'gujarati magazine'],
    'kn': ['kannada', 'kannada news', 'kannada tv', 'kannada magazine']
}


def get_common_words(lang):
    name = LC_NAME[lang]
    fname = '1000-most-common-words/1000-most-common-{}-words.txt'.format(name)
    with open(fname) as f:
        words = f.read().split()
    return list(filter(lambda s: (len(s) > 4), words))[:10]


def check_page(url, lang):
    content = requests.get(url).content
    isReliable, textBytesFound, details = cld2.detect(content)
    for lname, lcode, conf, _ in details:
        if lcode == lang:
            return True
    return False


def get_source_size(url):
    params = urllib.parse.urlencode({'q': 'site:{}'.format(url)})
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    }
    res = requests.get('https://www.google.com/search?' + params,
                       headers=headers)
    match = re.search('About ([0-9,]*) results', res.text)
    return int(match.group(1).replace(',', ''))


def build_search_terms(lang):
    terms = get_common_words(lang) + keywords[lang]
    return terms


def extract_urls(lang):
    terms = build_search_terms(lang)[:1]
    urls = set()
    for term in terms:
        # print('Searching term: ', term)
        next_urls = list(search(term, stop=10))
        urls.update(map(lambda u: urlparse(u).scheme + '://' + urlparse(u).netloc, next_urls))
        time.sleep(1)

    urls = list(urls)
    print(urls)
    for url in urls:
        try:
            # print('Validating url: ', url)
            lang_correct = check_page(url, lang)
            size = get_source_size(url)
            # print('Lang matches: ', lang_correct)
            # print('Estimated source size: ', size)
            if lang_correct and size > 100000:
                print(url)
        except:
            pass


extract_urls('kn')
