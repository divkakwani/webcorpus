import click
import logging

from .corpus.stats import print_stats
from .crawlers.processes import fetch_corpus


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    if debug:
        click.echo('Debug mode is ON')


@cli.command(name='getsources')
@click.option('--lang', required=True)
@click.option('--srcdir', required=True)
def get_sources(lang, srcdir):
    pass


@cli.command(name='fetch')
@click.option('--lang', required=True)
@click.option('--srcdir', required=True)
@click.option('--jobdir_root', required=True)
@click.option('--output', required=True)
@click.option('--logfile', default=None)
def fetch(lang, srcdir, jobdir_root, output, logfile):
    if logfile:
        logging.basicConfig(filename=logfile)
    else:
        logging.basicConfig(level=logging.WARN)
    fetch_corpus(lang, output, srcdir, jobdir_root)


@cli.command(name='stats')
@click.option('--corpus', required=True)
def stats(corpus):
    print_stats(corpus)


if __name__ == "__main__":
    cli()
