import click
import logging

from scrapy.crawler import CrawlerProcess
from .corpus.stats import print_stats
from .crawlers.w3newspaper import W3NewsPaperSpider
from .crawlers.news import RecursiveSpider
from .processors.arts import ArtsProcessor
from .processors.sent import SentProcessor


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    if debug:
        click.echo('Debug mode is ON')


@cli.command(name='getsources')
@click.option('--langs', required=True)
@click.option('--srcdir', required=True)
def get_sources(langs, srcdir):
    langs = langs.split(',')
    process = CrawlerProcess()
    process.crawl(W3NewsPaperSpider, srcdir=srcdir, languages=langs)
    process.start()


@cli.command(name='fetch')
@click.option('--lang', required=True)
@click.option('--source_name', required=True)
@click.option('--html_path', required=True)
@click.option('--home_url', required=True)
@click.option('--log_path', required=True)
def fetch(lang, source_name, html_path, home_url, log_path):
    process = CrawlerProcess()
    process.crawl(RecursiveSpider, lang=lang, source_name=source_name,
                  html_path=html_path, home_url=home_url, log_path=log_path)
    process.start()


@cli.command(name='process')
@click.option('--lang', required=True)
@click.option('--dtype', required=True)
@click.option('--input', required=True)
@click.option('--output', required=True)
def process(lang, dtype, input, output):
    if dtype == 'arts':
        processor = ArtsProcessor(lang, input, output)
    elif dtype == 'sent':
        processor = SentProcessor(lang, input, output)
    processor.gen_dataset()


@cli.command(name='stats')
@click.option('--corpus', required=True)
def stats(corpus):
    print_stats(corpus)


if __name__ == "__main__":
    cli()
