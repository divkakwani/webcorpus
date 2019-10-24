import click
import logging
import os
import warnings

warnings.filterwarnings("ignore")
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("tldextract").setLevel(logging.ERROR)

from scrapy.crawler import CrawlerProcess
from .crawlers import W3NewsPaperSpider
from .crawlers import makecrawler
from .corpus import CorpusProcessor
from .sources import SourceList


DATASTORE_PATH = os.environ.get('DATASTORE')
if DATASTORE_PATH is None:
    os.environ['DATASTORE'] = os.path.join(os.environ.get('HOME'), 'datastore')
    DATASTORE_PATH = os.environ.get('DATASTORE')


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    if debug: click.echo('Debug mode is ON')


@cli.command(name='fetch-sources')
def fetch_sources():
    process = CrawlerProcess()
    process.crawl(W3NewsPaperSpider)
    process.start()


@cli.command(name='fetch-news')
@click.option('--lang', required=True)
@click.option('--srange', default=None)
@click.option('--timeout', default=0)
@click.option('--download-delay', default=0.05)
@click.option('--verbose/--no-verbose', default=False)
def download_news(lang, srange, timeout, download_delay, verbose):
    # prepare list of sources
    source_list = SourceList(lang)
    sources = [source for source in source_list]
    sources = sorted(sources, key=lambda s: s['id'])
    if srange is not None:
        start, end = list(map(int, srange.split(',')))
        sources = sources[start:end]
    sources = list(filter(lambda s: s['active'], sources))
    if verbose: print('<<< RUNNING IN VERBOSE MODE >>>')
    print("Crawling sources: ", sources)

    # create job directories
    jobdirs = {}
    for source in sources:
        name = source['name']
        jobdir = os.path.join(DATASTORE_PATH, 'jobs/current', name)
        jobdirs[name] = jobdir
        os.makedirs(jobdir, exist_ok=True)

    process = CrawlerProcess(settings={
        'CLOSESPIDER_TIMEOUT': int(timeout),
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
    })
    for source in sources:
        crawler = makecrawler(source, JOBDIR=jobdirs[source['name']],
                              DUPEFILTER_DEBUG=verbose, DOWNLOAD_DELAY=download_delay)
        if crawler:
            process.crawl(crawler, source=source, datadir=DATASTORE_PATH)
    process.start()  # block until all crawling jobs are finished
    return

@cli.command(name='detect-inactives')
@click.option('--lang', required=True)
@click.option('--threshold', required=True)
def detect_inactives(lang, threshold):
    """After crawling raw data for say an hr, disable all the sources with `data_count < threshold`
    
    Recommended threshold: atleast 50 (if you ran for an hour)
    """
    src_list = SourceList(lang)
    src_list.disable_inactives(DATASTORE_PATH, int(threshold))
    return

@cli.command(name='process-news')
@click.option('--corpuspath')
@click.option('--lang')
@click.option('--fmt', default='json')
def process_datasets(corpuspath, lang, fmt):
    op_path = os.path.join(DATASTORE_PATH, 'processed', lang)
    processor = CorpusProcessor(corpuspath, lang, fmt, op_path)
    processor.process()


if __name__ == "__main__":
    cli()
