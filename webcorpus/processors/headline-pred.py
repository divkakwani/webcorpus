"""
Copyright © Divyanshu Kakwani 2019, all rights reserved.

Create a sentence file from an article corpus

"""
import json
import string
import asyncio
import aiohttp
import shelve
import random

from threading import Thread
from requests import get
from time import sleep
from functools import reduce
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
        self.cache = shelve.open('entity_cache', writeback=True)
        if 'words' not in self.cache:
            self.cache['words'] = {}
            self.cache.sync()
        self.URL = 'https://www.wikidata.org/w/api.php?action=wbsearchentities'\
                          '&search={}&language={}&format=json'
        self.num_http_calls = 0
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

        self.cache.sync()

        return entities


class HeadlinesProcessor:

    def __init__(self, lang, input_path, output_path):
        self.lang = lang
        self.script = code2script(lang)
        self.input_corpus = CatCorpus(input_path)
        normalizer_factory = IndicNormalizerFactory()
        self.normalizer = normalizer_factory.get_normalizer(self.lang)
        self.wikient = WikiEntities(self.lang)

    def _strip_title(self, txt):
        txt = txt.strip()
        neg_letter = string.ascii_letters + '| '
        s, e = 0, len(txt) - 1
        if self.lang != 'en':
            while txt[s] in neg_letter:
                s += 1
            while txt[e] in neg_letter:
                e -= 1
        return txt[s:e]

    def extract_words(self, txt):
        sents = sentence_split(txt, self.lang)
        words = []
        for sent in sents:
            newline_removed = sent.replace('\n', ' ')
            normalized = self.normalizer.normalize(newline_removed)
            words += trivial_tokenize(normalized, self.lang)
        return words

    def gen_dataset(self):
        articles = []
        for cat, iden, payload in tqdm(self.input_corpus.files()):
            article = json.loads(payload)
            articles.append(json.loads(payload))

            if len(articles) == 10000:
                break

        articles = articles[:200]
        ent_sets = []

        for i, art in enumerate(articles):
            words = self.extract_words(art['body'])
            eset = self.wikient.extract_entities(words)
            ent_sets.append(eset)
            print('Processed {} articles. Wikidata API calls: {}, Cache hits: {}'\
                  .format(i + 1, self.wikient.num_http_calls, self.wikient.cache_hits))

        minhashes = [MinHash(num_perm=128) for i in range(len(articles))]

        for i, eset in enumerate(ent_sets):
            for elm in eset:
                minhashes[i].update(elm.encode('utf-8'))

        lsh = MinHashLSH(threshold=0.4, num_perm=128)
        for i, minhash in enumerate(minhashes):
            lsh.insert(i, minhash)

        instances = []
        for i in range(len(articles)):
            results = lsh.query(minhashes[i])
            correct_title = (i, self._strip_title(articles[i]['title']))
            if len(correct_title[1]) == 0:
                break
            if len(results) >= 4:
                cand_titles = [(rid, self._strip_title(articles[rid]['title'])) for rid in results]
                cand_titles = list(filter(lambda x: len(x[1]) > 0, cand_titles))
                new_cand_titles = [correct_title]
                id1 = correct_title[0]
                for id2, title in cand_titles:
                    if minhashes[id1].jaccard(minhashes[id2]) <= 0.7:
                        new_cand_titles.append((id2, title))
                cand_titles = new_cand_titles
                if len(cand_titles) < 4:
                    continue
                cand_titles = cand_titles[:4]
                random.shuffle(cand_titles)
                correct_option = chr(ord('A') + cand_titles.index(correct_title))

                instance = {
                    'content': articles[correct_title[0]]['body'],
                    'correctOption': correct_option,
                    'optionA': cand_titles[0][1],
                    'optionB': cand_titles[1][1],
                    'optionC': cand_titles[2][1],
                    'optionD': cand_titles[3][1]
                }
                instances.append(instance)
        random.shuffle(instances)
        n = len(instances)
        s1, s2 = int(0.8*n), int(0.9*n)
        train = instances[:s1]
        valid = instances[s1:s2]
        test = instances[s2:]
        json.dump(instances, open('train.json', 'w'), ensure_ascii=False, indent=4, sort_keys=True)
        json.dump(instances, open('valid.json', 'w'), ensure_ascii=False, indent=4, sort_keys=True)
        json.dump(instances, open('test.json', 'w'), ensure_ascii=False, indent=4, sort_keys=True)


p = HeadlinesProcessor('kn', '/home/divkakwani/Downloads/sanmarg', '/home/divkakwani/temp')
p.gen_dataset()
