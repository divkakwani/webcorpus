"""
Copyright © Divyanshu Kakwani 2019, all rights reserved.

Create a sentence file from an article corpus

"""
import json
import os
import string
import shelve
import sys
import copy
import regex
import random
import unicodedata as ud

from threading import Thread
from requests import get
from time import sleep
from functools import reduce
from itertools import filterfalse
from tqdm import tqdm
from urllib.parse import quote
from ..corpus.io import CatCorpus, SentCorpus
from ..language.normalize import IndicNormalizerFactory
from ..language.tokenize import trivial_tokenize
from ..language.sentence_tokenize import sentence_split
from ..language import code2script, in_script
from datasketch import MinHash, MinHashLSH


class URLThread(Thread):
    def __init__(self, url):
        super(URLThread, self).__init__()
        self.url = url
        self.response = None

    def run(self):
        self.response = get(self.url)


def multi_get(uris, timeout=2.0):
    def alive_count(lst):
        alive = map(lambda x: 1 if x.isAlive() else 0, lst)
        return reduce(lambda a,b: a+b, alive, 0)
    threads = [URLThread(uri) for uri in uris]
    for thread in threads:
        thread.start()
    while alive_count(threads) > 0 and timeout > 0.0:
        timeout = timeout - 0.01
        sleep(0.01)
    return [(x.url, x.response) for x in threads]


class WikiEntities:

    def __init__(self, lang):
        # Load cache
        self.cache_fname = '{}-words.json'.format(lang)
        if os.path.exists(self.cache_fname):
            with open(self.cache_fname) as fp:
                self.cache = json.load(fp)
        else:
            self.cache = {'words': {}}

        self.URL = 'https://www.wikidata.org/w/api.php?action=wbsearchentities'\
                          '&search={}&language={}&format=json'
        self.num_http_calls = 0
        self.last_sync = 0
        self.cache_hits = 0
        self.lang = lang

    def _is_entity(self, response, word):
        try:
            result = response.json()
            matches = [item['match']['text'] for item in result['search']]
            if word in matches:
                return True
            return False
        except:
            return False

    def extract_entities(self, words):
        entities = set()
        url2word = {}
        for word in words:
            if word in self.cache['words']:
                self.cache_hits += 1
                if self.cache['words'][word]:
                    entities.add(word)
            elif word not in self.cache and len(word) > 2:
                url2word[self.URL.format(quote(word), self.lang)] = word

        self.num_http_calls += len(url2word)
        ret = multi_get(url2word.keys())

        for url, response in ret:
            word = url2word[url]
            is_ent = self._is_entity(response, word)
            self.cache['words'][word] = is_ent
            if is_ent:
                entities.add(word)

        if self.num_http_calls - self.last_sync > 1000:
            with open(self.cache_fname, 'w') as fp:
                json.dump(self.cache, fp, ensure_ascii=False, indent=4)
            self.last_sync = self.num_http_calls

        return entities


class ArticlesDatabase:
    
    def __init__(self, lang):
        self.lang = lang
        self.wikient = WikiEntities(self.lang)
        normalizer_factory = IndicNormalizerFactory()
        self.normalizer = normalizer_factory.get_normalizer(self.lang)
        self.articles = []
        self.ent_sets = []
        self.minhashes = []
        self.lsh = MinHashLSH(threshold=0.5, num_perm=128)

    def __getitem__(self, key):
        return self.articles[key]

    def __len__(self):
        return len(self.articles)

    def __iter__(self):
        self.it_idx = 0
        return self

    def __next__(self):
        self.it_idx += 1
        if self.it_idx > len(self.articles):
            raise StopIteration
        return self.articles[self.it_idx-1]
    
    def extract_words(self, txt):
        sents = sentence_split(txt, self.lang)
        words = []
        for sent in sents:
            newline_removed = sent.replace('\n', ' ')
            normalized = self.normalizer.normalize(newline_removed)
            words += trivial_tokenize(normalized, self.lang)
        return words

    def add(self, article):
        index = len(self.articles)
        minhash = self.compute_hash(article)

        if (index+1) % 1000 == 0:
            print('Processed {} articles. Wikidata API calls: {}, Cache hits: {}'\
                  .format(index + 1, self.wikient.num_http_calls, self.wikient.cache_hits))

        self.articles.append(article)
        self.minhashes.append(minhash)

        self.lsh.insert(index, minhash)

    def count(self):
        return len(self.titles)

    def compute_hash(self, article):
        words = self.extract_words(article['title'] + ' ' + article['body'])
        eset = self.wikient.extract_entities(words)
        minhash = MinHash(num_perm=128)
        for elm in eset:
            minhash.update(elm.encode('utf-8'))
        return minhash

    def query_similar(self, art, nmax=3):
        """
        returns a list of indices that correspond to similar articles
        The following conditions are maintained:
        * the retuned list does not contain the original article
        * No two articles in the list have the same title
        * For any two articles x, y in the list, the similarity is within (0.5, 0.8)
        """
        title_set = set(art['title'])
        minhash = self.compute_hash(art)
        indices = self.lsh.query(minhash)
        results = []

        for midx in indices:
            if len(results) >= nmax:
                break
            # make sure title does not repeat
            if art['title'] in title_set:
                continue

            # make sure the article is not too similar to any other article
            # in fresutls
            is_similar = False
            if minhash.jaccard(self.minhashes[midx]) > 0.8:
                is_similar = True
            for art_idx in results:
                if self.minhashes[art_idx].jaccard(self.minhashes[midx]) > 0.8:
                    is_similar = True
            if is_similar:
                continue

            results.append(midx)

        matched_arts = map(lambda i: self.articles[i], results)
        matched_arts = list(matched_arts)
        return matched_arts


class HeadlinesProcessor:

    def __init__(self, lang, input_path, output_path):
        self.lang = lang
        self.script = code2script(lang)
        self.input_corpus = CatCorpus(input_path)
        self.artdb = ArticlesDatabase(self.lang)

    def _strip_txt(self, txt):
        txt = txt.strip()
        neg_letter = string.digits + string.ascii_letters + string.punctuation + string.whitespace
        s, e = 0, len(txt) - 1
        if self.lang != 'en':
            while s < len(txt) and txt[s] in neg_letter:
                s += 1
            while e >= 0 and txt[e] in neg_letter:
                e -= 1
        return txt[s:e+1]

    def clean_article(self, art):
        # remove unneccesary fields in the title like newspaper name etc.
        titles = art['title'].split('|')
        art['title'] = max(titles, key=len)
            
        # remove title from the body content
        # boilerpipe tends to include the title also in the body content
        pattern = regex.compile('({}){{e<=5}}'.format(regex.escape(art['title'])))
        match = pattern.search(art['body'])
        if match:
            end_idx = match.span()[1]
            art['body'] = art['body'][end_idx:]

        art['title'] = self._strip_txt(art['title']) 
        art['body'] = self._strip_txt(art['body']) 

        return art


    def gen_dataset(self):
        for cat, iden, payload in tqdm(self.input_corpus.files()):
            art = json.loads(payload)

            if not art['title']:
                continue

            art = self.clean_article(art)

            if len(art['title']) > 20 and len(art['body']) in range(200, 2000):
                self.artdb.add(art)

            if len(self.artdb) == 200000:
                break

        instances = []

        for art in self.artdb:
            similar = self.artdb.query_similar(art)

            if len(similar) < 3:
                continue

            cand_titles = [art['title']] + list(map(lambda a: a['title'], similar[:3]))
            random.shuffle(cand_titles)
            correct_option = chr(ord('A') + cand_titles.index(art['title']))

            instance = {
                'content': art['body'],
                'correctOption': correct_option,
                'articleURL': art['url'],
                'optionA': cand_titles[0],
                'optionB': cand_titles[1],
                'optionC': cand_titles[2],
                'optionD': cand_titles[3]
            }
            instances.append(instance)

            n = len(instances)
            if n % 100 == 0:
                print('Generated {} instances'.format(n))

        random.shuffle(instances)
        instances = instances[:100000]
        n = len(instances)
        s1, s2 = int(0.8*n), int(0.9*n)
        train = instances[:s1]
        valid = instances[s1:s2]
        test = instances[s2:]
        json.dump(train, open('{}-train.json'.format(self.lang), 'w'), ensure_ascii=False, indent=4, sort_keys=True)
        json.dump(valid, open('{}-valid.json'.format(self.lang), 'w'), ensure_ascii=False, indent=4, sort_keys=True)
        json.dump(test, open('{}-test.json'.format(self.lang), 'w'), ensure_ascii=False, indent=4, sort_keys=True)


lang = sys.argv[1]
print('Processing lang: ', lang)
p = HeadlinesProcessor(lang, '/media/divkakwani/drive/{}-articles'.format(lang), '/home/divkakwani/temp')
p.gen_dataset()
