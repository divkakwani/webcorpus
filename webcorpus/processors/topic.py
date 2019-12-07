"""
Copyright © Divyanshu Kakwani 2019, all rights reserved.

Creates text classification dataset from a news article corpus

"""
import json

from tqdm import tqdm
from ..corpus import CatCorpus


# TODO: use wor2word

topic_synsets = {
    'entertainment': ['entertainment', 'cinema', 'bollywood', 'film', 'tv',
                      'cinema-news', 'movies', 'manoranjan',
                      'manoranjan-news'],
    'politics': ['politics', 'election'],
    'business':  ['business', 'business-news', 'kannada-business-news',
                  'stockmarket', 'money'],
    'crime': ['crime', 'crime-news'],
    'technology': ['technology', 'tech', 'gadgets'],
    'astrology':  ['astrology', 'astro', 'astro-news', 'astrology-news',
                   'horoscope'],
    'sports':   ['sports', 'cricket', 'football', 'krida', 'krida-news',
                 'krida-cricket'],
    'lifestyle': ['lifestyle', 'life-style', 'health', 'health-tips',
                  'lifestyle-news'],
    'auto': ['auto', 'automobile'],
    'agriculture': ['agriculture', 'agro']
}
min_len = 200


def gen_dataset(*args, **kwargs):
    """
    """
    topics = kwargs.get('topics', None)
    max_samples = kwargs.get('max_samples', 20000)
    input_path = kwargs.get['input_path']
    output_path = kwargs.get['output_path']

    if not topics:
        topics = topic_synsets.keys()

    samples_seen = {t: 0 for t in topics}
    in_corpus = CatCorpus(input_path)
    out_corpus = CatCorpus(output_path)

    for content in tqdm(in_corpus.files()):
        article = json.loads(content)

        # find article's topic
        topic = None
        for tr in topic_synsets:
            for tv in topic_synsets[tr]:
                if '/{}/'.format(tv) in article['url']:
                    topic = tr
                    break

        if topic:
            txt = article['content']
            if len(txt) >= min_len and samples_seen[topic] < max_samples:
                samples_seen[topic] += 1
                out_corpus.add_file(topic, samples_seen[topic], txt)
