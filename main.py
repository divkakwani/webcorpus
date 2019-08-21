
import click
import json

from crawlers import W3NewsPaperSpider
from crawlers import make_news_crawler
from scrapy.crawler import CrawlerProcess


SOURCES_PATH = './data/news_sources.json'


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo('Debug mode is %s' % ('on' if debug else 'off'))


@cli.command(name="fetch-sources")
def fetch_urls():
    W3NewsPaperSpider.disk_path = SOURCES_PATH
    process = CrawlerProcess()
    process.crawl(W3NewsPaperSpider)
    process.start()


def load_urls(disk_path):
    with open(disk_path) as fp:
        urls = json.load(fp)
    return [(l, u) for l in urls for u in urls[l]]


@cli.command(name="fetch-news")
@click.option('--lang', default=None)
def download_news(lang):
    sources = load_urls(SOURCES_PATH)
    if lang:
        sources = filter((lambda e: e[0] == lang), sources)
    process = CrawlerProcess()
    for lang, url in sources:
        process.crawl(make_news_crawler(lang, url))
    process.start()  # block until all crawling jobs are finished


@cli.command(name="process-news")
def process_datasets(corpus_path, lang):
    pass
    # processor = NewsCorpusProcessor(corpus_path, lang)


if __name__ == '__main__':
    cli()
