"""
Copyright © Divyanshu Kakwani 2019, all rights reserved.

Creates text classification dataset from a news article corpus

"""
import json

from tqdm import tqdm
from ..corpus import NewsCorpus, FileCorpus


topic_synsets = {
    'entertainment': ['entertainment', 'cinema', 'bollywood', 'film', 'tv',
                      'cinema-news', 'movies', 'manoranjan',
                      'manoranjan-news'],
    'politics': ['politics', 'election'],
    'business':  ['business', 'business-news', 'kannada-business-news',
                  'stockmarket', 'money', 'business-economy'],
    'crime': ['crime', 'crime-news'],
    'technology': ['technology', 'tech', 'gadgets', 'science-technology'],
    'astrology':  ['astrology', 'astro', 'astro-news', 'astrology-news',
                   'horoscope'],
    'sports':   ['sports', 'cricket', 'football', 'krida', 'krida-news',
                 'krida-cricket'],
    'lifestyle': ['lifestyle', 'life-style', 'health', 'health-tips',
                  'lifestyle-news'],
    'auto': ['auto', 'automobile'],
    'agriculture': ['agriculture', 'agro']
}

class TopicProcessor:

    def __init__(self, lang, input_path, output_path):
        self.lang = lang
        self.input_corpus = NewsCorpus(lang, input_path)
        self.output_corpus = FileCorpus(lang, output_path, encoding='csv')

    def run(self):
        samples_seen = {t: 0 for t in topics}
        min_len, max_samples = 200, 20000
        for article in tqdm(self.input_corpus.all_instances()):
            # find article's topic
            topic = None
            for tr in topic_synsets:
                for tv in topic_synsets[tr]:
                    if '/{}/'.format(tv) in article['url']:
                        topic = tr
                        break
            if topic:
                txt = article['body']
                if len(txt) >= min_len and samples_seen[topic] < max_samples:
                    self.output_corpus.add_instance([topic, txt])