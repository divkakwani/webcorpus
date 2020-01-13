"""
Copyright © Divyanshu Kakwani 2019, all rights reserved

Defines general spiders for news sources

There are two general spiders: RecursiveSpider and SitemapSpider. The
former starts at the home page and recursively follows all the links. The
latter extracts all the urls from the sitemap and then simply pulls those urls
without following further links found in the page.

Custom spiders are needed to handle irregular news sources. A custom spider
should have a name in the format <Source Name>Spider. e.g. SahilonlineSpider
and it should inherit from one of the general spider and override whatever
functionality it wants to override

"""
import scrapy
import json
import os
import tldextract

from boilerpipe.extract import Extractor
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from datetime import datetime
from twisted.internet import task
from ..corpus.io import CatCorpus
from ..language import code2script, in_script


class BaseNewsSpider(scrapy.Spider):

    name = 'base-news-spider'

    def __init__(self, *args, **kwargs):
        self.lang = kwargs['lang']
        self.script = code2script(self.lang)
        self.name = kwargs['source_name']
        self.arts_path = kwargs['arts_path']
        self.html_path = kwargs['html_path']
        self.home_url = kwargs['home_url']
        self.log_path = kwargs['log_path']
        self.extract_arts = kwargs.get('extract_article', False)
        self.arts_collected = 0
        self.pages_crawled = 0

        os.makedirs(self.arts_path, exist_ok=True)
        os.makedirs(self.html_path, exist_ok=True)

        parts = tldextract.extract(self.home_url)
        domain = '{}.{}.{}'.format(parts.subdomain, parts.domain, parts.suffix)
        self.allowed_domains = [domain]

        self.arts_corpus = CatCorpus(self.arts_path)
        self.html_corpus = CatCorpus(self.html_path)

        super().__init__(self.name)

        self.log_file = os.path.join(self.log_path, 'stats', kwargs['_job'])
        call = task.LoopingCall(self.log_stats)
        call.start(300)  # call every 5 mins

    def log_stats(self):
        stats = {'lang': self.lang, 'source': self.name,
                 'pages_crawled': self.pages_crawled}
        with open(self.log_file, 'w') as fp:
            json.dump(stats, fp)

    def write_html(self, response):
        html = response.body.decode(response.encoding)
        html_page = {
            'html': html,
            'source': self.name,
            'url': response.request.url,
            'timestamp': datetime.now().strftime('%d/%m/%y %H:%M')
        }
        json_data = json.dumps(html_page)
        self.html_corpus.add_file(self.name, response.request.url, json_data)
        self.pages_crawled += 1

    def parse(self, response):
        raise NotImplementedError

    def closed(self, reason):
        print('Closing spider. Name: ', self.name, ' Reason: ', reason)


class SitemapSpider(BaseNewsSpider, scrapy.spiders.SitemapSpider):

    name = 'sitemap-spider'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sitemap_urls = [kwargs['sitemap_url']]

    def parse(self, response):
        self.write_html(response)


class RecursiveSpider(BaseNewsSpider):

    name = 'recursive-spider'

    def __init__(self, *args, **kwargs):
        self.start_urls = [kwargs['home_url']]
        self.link_extractor = LinkExtractor()
        super().__init__(*args, **kwargs)

    def parse(self, response):
        self.write_html(response)

        links = self.link_extractor.extract_links(response)
        for link in links:
            yield scrapy.Request(link.url)


class SanjevaniSpider(RecursiveSpider):
    """
    Boilerpipe does not work for this news source
    """

    name = 'sanjevani-spider'

    def extract_article_content(self, html):
        sel = Selector(text=html)
        text = ''
        for node in sel.css('.entry-content *::text'):
            text = text + '\n' + node.extract()
        return text


class AnupambharatonlineSpider(RecursiveSpider):

    name = 'anupambharatonline'

    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter'
    }
