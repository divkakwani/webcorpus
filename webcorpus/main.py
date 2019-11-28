import click

from .corpus.stats import print_stats


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
@click.option('--chkp_period', default=21600)
@click.option('--output', required=True)
@click.option('--output', required=True)
@click.option('--verbose/--no-verbose', default=False)
def fetch(lang, srcdir, jobdir_root, timeout, output, chkp_period,
          download_delay, verbose):
    pass


@cli.command(name='stats')
@click.option('--corpus', required=True)
def stats(corpus):
    print_stats(corpus)


if __name__ == "__main__":
    cli()
