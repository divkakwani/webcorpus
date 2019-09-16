
import click
import logging
import json
import warnings

warnings.filterwarnings("ignore")
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("tldextract").setLevel(logging.ERROR)

from crawlers import W3NewsPaperSpider
from crawlers import getcrawler
from corpus import NewsCorpusProcessor, CorpusMetadataManager
from scrapy.crawler import CrawlerProcess


SOURCES_PATH = './data/news_sources.json'


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo('Debug mode is %s' % ('on' if debug else 'off'))


@cli.command(name='fetch-sources')
def fetch_sources():
    W3NewsPaperSpider.disk_path = SOURCES_PATH
    process = CrawlerProcess()
    process.crawl(W3NewsPaperSpider)
    process.start()


def load_sources(disk_path):
    with open(disk_path) as fp:
        sources = json.load(fp)
    return [(l, s) for l in sources for s in sources[l]]


@cli.command(name='fetch-news')
@click.option('--lang', default=None)
@click.option('--srange', default=None)
def download_news(lang, srange):
    sources = load_sources(SOURCES_PATH)
    if lang:
        sources = list(filter((lambda e: e[0] == lang), sources))
    if srange is not None:
        start, end = list(map(int, srange.split(',')))
        sources = sources[start:end]
    process = CrawlerProcess()
    for lang, source in sources:
        crawler = getcrawler(source)
        if crawler:
            process.crawl(crawler, source=source)
    process.start()  # block until all crawling jobs are finished


@cli.command(name='process-news')
@click.option('--corpuspath')
@click.option('--lang')
def process_datasets(corpuspath, lang):
    processor = NewsCorpusProcessor(corpuspath, lang)
    processor.process()


@cli.command(name='stats')
@click.option('--corpuspath')
def compute_stats(corpuspath):
    metadata = CorpusMetadataManager()
    stats = metadata.compute_stats(corpuspath)
    print('\u2500'*40)
    print('Statistics of the Dataset:')
    print('\u2500'*40)
    for k, v in stats.items():
        print('{0:<20} {1}'.format(k, v))
        print('\u2500'*40)


if __name__ == '__main__':
    cli()
