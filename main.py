
import click
import logging
import json
import warnings

warnings.filterwarnings("ignore")
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("tldextract").setLevel(logging.ERROR)

from crawlers import W3NewsPaperSpider
from crawlers import getcrawler
from corpus import CorpusProcessor, CorpusMetadataManager
from scrapy.crawler import CrawlerProcess
from sources import SourceList


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo('Debug mode is %s' % ('on' if debug else 'off'))


@cli.command(name='fetch-sources')
def fetch_sources():
    process = CrawlerProcess()
    process.crawl(W3NewsPaperSpider)
    process.start()


@cli.command(name='fetch-news')
@click.option('--lang', required=True)
@click.option('--srange', default=None)
@click.option('--timeout', default=0)
def download_news(lang, srange, timeout):
    # prepare list of sources
    source_list = SourceList(lang)
    sources = [source for source in source_list]
    sources = sorted(sources, key=lambda s: s['id'])
    if srange is not None:
        start, end = list(map(int, srange.split(',')))
        sources = sources[start:end]
    sources = list(filter(lambda s: s['active'], sources))
    print("Crawling sources: ", sources)

    process = CrawlerProcess(settings={
        'CLOSESPIDER_TIMEOUT': int(timeout),
        'JOBDIR': 'data/job'
    })
    for source in sources:
        crawler = getcrawler(source)
        if crawler:
            process.crawl(crawler, source=source)
    process.start()  # block until all crawling jobs are finished


@cli.command(name='process-news')
@click.option('--corpuspath')
@click.option('--lang')
@click.option('--fmt', default='json')
def process_datasets(corpuspath, lang, fmt):
    processor = CorpusProcessor(corpuspath, lang, fmt)
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
