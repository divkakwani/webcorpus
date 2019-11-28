
import json

from tqdm import tqdm
from ..corpus import CatCorpus


topic_synsets = {
    'entertainment': ['entertainment', 'cinema', 'bollywood', 'film', 'tv',
                      'cinema-news'],
    'politics': ['politics'],
    'business':  ['business', 'business-news', 'kannada-business-news',
                  'stockmarket'],
    'crime': ['crime', 'crime-news'],
    'technology': ['technology', 'tech'],
    'astrology':  ['astrology', 'astro', 'astro-news'],
    'sports':   ['sports', 'cricket', 'football'],
    'lifestyle': ['lifestyle', 'life-style', 'health']
}


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
            if len(txt) >= 300 and samples_seen[topic] < max_samples:
                samples_seen[topic] += 1
                out_corpus.add_file(topic, samples_seen[topic], txt)
