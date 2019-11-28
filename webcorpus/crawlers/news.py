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

from boilerpipe.extract import Extractor
from scrapy.linkextractors import LinkExtractor
from ..corpus import CatCorpus, Article
from ..utils import url_validate
from ..utils import langcode2script, in_script


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
    if url_validate(source["sitemap_url"]):
        try:
            response = requests.get(source["sitemap_url"])
            if response.status_code == 200:
                return SitemapSpider
        except requests.exceptions.ConnectionError:
            pass

    # check for recursive spider
    try:
        response = requests.get(source["home_url"])
        if response.status_code == 200 or response.status_code == 406:
            return RecursiveSpider
    except requests.exceptions.ConnectionError:
        pass

    return None


def makecrawler(source, srcdir, **settings):
    """
    creates a new spider class by cloning one of the base classes
    and then populating the custom settings appropriately
    """
    sys.path.append(srcdir)
    globals().update(importlib.import_module('custom_handlers').__dict__)

    baseclass = _select_baseclass(source)
    if baseclass is None:
        return None

    # clone the blueprint
    spidername = source['name'].capitalize() + 'Final' + 'Spider'
    spidercls = type(spidername, (baseclass,), {})

    # populate class variables
    if spidercls.custom_settings is None:
        spidercls.custom_settings = {}
    spidercls.custom_settings.update(settings)

    return spidercls


class BaseNewsSpider(scrapy.Spider):

    custom_settings = {
        "DOWNLOAD_DELAY": 0.05,
        "LOG_ENABLED": False,
        "CONCURRENT_REQUESTS": 64,
        "AUTOTHROTTLE_ENABLED": True,
    }

    def __init__(self, source, corpus_path):
        self.lang = source["lang"]
        self.script = langcode2script(self.lang)
        self.name = source["name"]

        os.makedirs(self.corpus_path, exist_ok=True)

        parts = tldextract.extract(source["home_url"])
        domain = "{}.{}.{}".format(parts.subdomain, parts.domain, parts.suffix)
        self.allowed_domains = [domain]

        self.corpus = CatCorpus(self.corpus_path)

        super().__init__(self.name)

    def extract_article_content(self, html):
        extractor = Extractor(extractor="ArticleExtractor", html=html)
        text = extractor.getText()
        return text

    def parse_article(self, response):
        """
        Extracts the article content from the response body and prepares
        the article object
        """
        text = self.extract_article_content(response.body)
        if self._is_article(text):
            article = Article(
                content=text,
                source=self.name,
                url=response.request.url,
                raw_html=response.body,
            )
            return article
        return None

    def _is_article(self, text, win_sz=300, thres=260):
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
        dump = json.dumps(article, indent=4)
        self.corpus.add_file(article["source"], article["url"], dump)

    def parse(self, response):
        raise NotImplementedError


class SitemapSpider(BaseNewsSpider, scrapy.spiders.SitemapSpider):
    def __init__(self, source, datadir):
        super().__init__(source, datadir)
        self.sitemap_urls = [source['sitemap_url']]

    def parse(self, response):
        article = self.parse_article(response)
        if article:
            self.write_article(article)


class RecursiveSpider(BaseNewsSpider):
    def __init__(self, source, datadir):
        self.start_urls = [source['home_url']]
        self.link_extractor = LinkExtractor()
        super().__init__(source, datadir)

    def parse(self, response):
        article = self.parse_article(response)
        if article:
            self.write_article(article)

        links = self.link_extractor.extract_links(response)
        for link in links:
            yield scrapy.Request(link.url)
