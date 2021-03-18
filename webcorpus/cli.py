#!/usr/bin/env python3

import click
import logging
import requests
import time
import os
import subprocess

from termcolor import cprint
from scrapyd.scripts.scrapyd_run import main as scrapyd_main

from webcorpus.crawlers.w3newspaper import W3NewsPaperSpider
from webcorpus.crawlers.news import RecursiveSpider
from webcorpus.processors.arts import ArtsProcessor
from webcorpus.processors.sent import SentProcessor


def scrapyd_query(url, **kwargs):
    argstring = ''
    for k in kwargs:
        argstring += f' -d {k}={kwargs[k]}'
    print(url + argstring)
    response = requests.get(url + argstring, timeout=10)
    return response.json()


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    if debug:
        click.echo('Debug mode is ON')


@cli.command(name='start')
@click.option('--port', required=False)
def start(port):
    cprint('Starting Server...', 'white', attrs=['bold'])
    os.makedirs('logs', exist_ok=True)
    subprocess.Popen(['scrapyd'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    subprocess.Popen(['scrapyd-deploy'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    time.sleep(5)
    try:
        response = requests.get('http://localhost/daemonstatus.json')
        cprint('Started scrapyd server successfully', 'green', attrs=['bold'])
    except:
        cprint('Failed to start scrapyd server', 'red', attrs=['bold'])


@cli.command(name='crawl')
@click.option('--path', required=True)
@click.option('--name', required=True)
@click.option('--url', required=True)
@click.option('--log', required=True)
def crawl(path, name, url, log):
    try:
        data = {
            'project': 'webcorpus',
            'spider': 'recursive-spider',
            'html_path': path,
            'source_name': name,
            'home_url': url,
            'lang': 'en',
            'log_path': log
        }
        status = requests.post('http://localhost/schedule.json', data=data)
        cprint('Crawl started', 'green', attrs=['bold'])
    except Exception as e:
        print(e)
        cprint('Failed to start the crawl', 'red', attrs=['bold'])


@cli.command(name='process')
@click.option('--operation', required=True)
@click.option('--lang', required=True)
@click.option('--input', required=True)
@click.option('--output', required=True)
def process(operation, lang, input, output):
    if operation == 'extract_arts':
        proc = ArtsProcessor(lang, input, output) 
    elif operation == 'extract_sents':
        proc = SentProcessor(lang, input, output) 
    elif operation == 'extract_genres':
        proc = TopicProcessor(lang, input, output) 
    else:
        cprint('Invalid operation', 'red', attrs=['bold'])
    proc.run()


if __name__ == "__main__":
    cli()
