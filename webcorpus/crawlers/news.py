"""
Copyright © Divyanshu Kakwani 2019, all rights reserved

Defines general spiders for news sources

There are two general spiders: RecursiveSpider and NewsSitemapSpider. The
former starts at the home page and recursively follows all the links. The
latter extracts all the urls from the sitemap and then simply pulls those urls
without following further links found in the page.

Custom spiders are needed to handle irregular news sources. A custom spider
should have a name in the format <Source Name>Spider. e.g. SahilOnlineSpider
and it should inherit from one of the general spider and override whatever
functionality it wants to override

"""
import scrapy
import json
import os
import requests
import tldextract
import sys
import inspect
import importlib
import re

from boilerpipe.extract import Extractor
from scrapy.linkextractors import LinkExtractor
from scrapy.linkextractors import Selector
from datetime import datetime
from ..corpus.io import CatCorpus
from ..language import code2script, in_script
from ..utils import validate_url
from ..remote import RemoteChannel


def _select_baseclass(source):
    """
    dynamically selects spider class based on the source
    """
    # check for a custom spider
    classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    mangled_name = (source['name'] + 'spider').lower()
    for cls_name, clas in classes:
        if mangled_name == cls_name.lower():
            return clas

    # check for the sitemap spider
    if source['use_sitemap'] and validate_url(source['sitemap_url']):
        try:
            response = requests.get(source['sitemap_url'])
            if response.status_code == 200:
                return SitemapSpider
        except requests.exceptions.ConnectionError:
            pass

    # check for recursive spider
    try:
        response = requests.get(source['home_url'], timeout=60)
        if response.status_code == 200 or response.status_code == 406:
            return RecursiveSpider
    except requests.exceptions.ConnectionError:
        pass

    return None


def makecrawler(source, **settings):
    """
    creates a new spider class by cloning one of the base classes
    and then populating the custom settings appropriately
    """
    baseclass = _select_baseclass(source)
    if baseclass is None:
        return None

    # clone the base class
    spidername = source['name'].capitalize() + 'Final' + 'Spider'
    spidercls = type(spidername, (baseclass,), {})

    # populate class variables
    if spidercls.custom_settings is None:
        spidercls.custom_settings = {}
    spidercls.custom_settings.update(settings)

    return spidercls


class BaseNewsSpider(scrapy.Spider):

    custom_settings = {
        'DOWNLOAD_DELAY': 0.05,
        'LOG_ENABLED': True,
        'CONCURRENT_REQUESTS': 1024,
        'AUTOTHROTTLE_ENABLED': True,
    }

    def __init__(self, source, arts_path, html_path):
        self.lang = source['lang']
        self.script = code2script(self.lang)
        self.name = source['name']
        self.arts_path = arts_path
        self.html_path = html_path
        self.remote_channel = RemoteChannel(self.name)
        self.arts_collected = 0

        os.makedirs(self.arts_path, exist_ok=True)
        os.makedirs(self.html_path, exist_ok=True)

        parts = tldextract.extract(source['home_url'])
        domain = '{}.{}.{}'.format(parts.subdomain, parts.domain, parts.suffix)
        self.allowed_domains = [domain]

        self.arts_corpus = CatCorpus(self.arts_path)
        self.html_corpus = CatCorpus(self.html_path)

        super().__init__(self.name)

    def extract_article_content(self, html):
        extractor = Extractor(extractor='ArticleExtractor', html=html)
        body = extractor.getText()
        title = extractor.source.title
        return {'title': title, 'body': body}

    def parse_article(self, response):
        """
        Extracts the article content from the response body and prepares
        the article object
        """
        content = self.extract_article_content(response.body)
        if self._is_article(content.body):
            article = {
                'title': content['title'],
                'body': content['body'],
                'source': self.name,
                'url': response.request.url,
                'timestamp': datetime.now().strftime('%d/%m/%y %H:%M')
            }
            return article
        return None

    def _is_article(self, text, win_sz=250, thres=200):
        """
        It performs two tests on the text to determine if the text represents
        a valid news article or not:
        1. Has length greater than `win_sz`
        2. Contains a continuous subtext of atleast length `win_sz` having
           atleast `thres` characters in the required language
        """
        txt_sz = len(text)
        if txt_sz < win_sz:
            return False

        chr_valid = [in_script(c, self.script) for c in text]
        subarr_sum = chr_valid.copy()
        for cur_sz in range(2, win_sz):
            subarr_sum = [
                chr_valid[i] + subarr_sum[i + 1] for i in range(txt_sz - cur_sz)
            ]
        if max(subarr_sum) >= thres:
            return True

        return False

    def write_article(self, article):
        dump = json.dumps(article, indent=4, ensure_ascii=False)
        self.arts_collected += 1
        if self.arts_colleced % 100 == 0:
            event = {'type': 'arts-count', 'lang': self.lang,
                     'source': self.name, 'count': self.arts_collected}
            self.remote_channel.send_event(event)
        self.arts_corpus.add_file(article['source'], article['url'], dump)

    def write_html(self, response):
        html = response.body.decode(response.encoding)
        self.html_corpus.add_file(self.name, response.request.url, html)

    def parse(self, response):
        raise NotImplementedError


class SitemapSpider(BaseNewsSpider, scrapy.spiders.SitemapSpider):
    def __init__(self, source, corpus_path):
        super().__init__(source, corpus_path)
        self.sitemap_urls = [source['sitemap_url']]

    def parse(self, response):
        article = self.parse_article(response)
        if article:
            self.write_article(article)
        self.write_html(response)


class RecursiveSpider(BaseNewsSpider):
    def __init__(self, source, corpus_path):
        self.start_urls = [source['home_url']]
        self.link_extractor = LinkExtractor()
        super().__init__(source, corpus_path)

    def parse(self, response):
        article = self.parse_article(response)
        if article:
            self.write_article(article)
        self.write_html(response)

        links = self.link_extractor.extract_links(response)
        for link in links:
            yield scrapy.Request(link.url)


def extract_links(text):
    return re.findall(r'(https?://[^\s"\\<>]+)', text)


class SanjevaniSpider(RecursiveSpider):
    """
    Boilerpipe does not work for this news source
    """

    def extract_article_content(self, html):
        sel = Selector(text=html)
        text = ''
        for node in sel.css('.entry-content *::text'):
            text = text + '\n' + node.extract()
        return text


class BalkaniNewsSpider(SitemapSpider):
    """
    The urls contained in the sitemap do not directly link to the page
    where the complete article exists
    """

    def __init__(self, source, corpus_path):
        super().__init__(source, corpus_path)
        self.link_extractor = LinkExtractor()

    def parse(self, response):
        article = self.parse_article(response)
        if article:
            self.write_article(article)
        self.write_html(response)

        links = self.link_extractor.extract_links(response)
        for link in links:
            yield scrapy.Request(link.url)


class AnupambharatonlineSpider(RecursiveSpider):
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter'
    }


class SahilOnlineSpider(BaseNewsSpider):
    """
    The sitemap is broken, invalid xml. But we can still extract the urls
    using scrapy's LinkExtractor
    """

    def __init__(self, source, corpus_path):
        response = requests.get(source['sitemap_url'])
        urls = extract_links(str(response.content))
        urls = list(filter(lambda u: not u.lower().endswith('jpg'), urls))
        self.start_urls = urls
        super().__init__(source, corpus_path)

    def parse(self, response):
        article = self.parse_article(response)
        if article:
            self.write_article(article)
        self.write_html(response)
