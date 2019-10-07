"""
Copyright © Divyanshu Kakwani 2019, all rights reserved

Defines general and custom spiders for news sources

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

from boilerpipe.extract import Extractor
from ..utils import url_validate, extract_links, page_name
from ..utils import langcode2name, langcode2script, in_script
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector


def _select_blueprint(source):
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
    if url_validate(source['sitemap_url']):
        response = requests.get(source['sitemap_url'])
        if response.status_code == 200:
            return NewsSitemapSpider

    # check for recursive spider
    response = requests.get(source['home_url'])
    if response.status_code == 200 or response.status_code == 406:
        return RecursiveSpider


def makecrawler(source, **settings):
    """
    creates a new spider class by cloning one of the blueprint classes
    and then populating the class variables appropriately
    """
    blueprint = _select_blueprint(source)
    if blueprint is None:
        return None

    # clone the blueprint
    spidername = source['name'].capitalize() + 'Final' + 'Spider'
    spidercls = type(spidername, (blueprint,), {})

    # populate class variables
    if spidercls.custom_settings is None:
        spidercls.custom_settings = {}
    spidercls.custom_settings.update(settings)

    return spidercls


class BaseNewsSpider(scrapy.Spider):

    custom_settings = {
        'DOWNLOAD_DELAY': 0.05,
        'LOG_ENABLED': False,
        'CONCURRENT_REQUESTS': 64,
        'AUTOTHROTTLE_ENABLED': True,
        'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': None,
    }

    def __init__(self, source, datadir):
        self.lang = source['language']
        self.lang_name = langcode2name(self.lang)
        self.script = langcode2script(self.lang)
        self.name = source['name']

        self.disk_path = os.path.join(datadir, 'raw', self.lang, self.name)
        os.makedirs(self.disk_path, exist_ok=True)

        components = tldextract.extract(source['home_url'])
        domain = components.domain + '.' + components.suffix
        self.allowed_domains = [domain]

        super().__init__(source['name'])

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
            article = {
                'name': page_name(response.url),
                'content': text,
                'source': response.request.url
            }
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
            subarr_sum = [chr_valid[i] + subarr_sum[i+1]
                          for i in range(txt_sz - cur_sz)]
        if max(subarr_sum) >= thres:
            return True

        return False

    def write_article(self, article):
        """
        writes articles to disk
        """
        fpath = os.path.join(self.disk_path, article['name'])
        with open(fpath, 'w', encoding='utf-8') as fp:
            json.dump(article, fp, indent=4, ensure_ascii=False)

    def parse(self, response):
        raise NotImplementedError


class NewsSitemapSpider(BaseNewsSpider, scrapy.spiders.SitemapSpider):

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


class BalkaniNewsSpider(NewsSitemapSpider):
    """
    The urls contained in the sitemap do not directly link to the page
    where the complete article exists
    """

    def __init__(self, source, datadir):
        super().__init__(source, datadir)
        self.link_extractor = LinkExtractor()

    def parse(self, response):
        article = self.parse_article(response)
        if article:
            self.write_article(article)

        links = self.link_extractor.extract_links(response)
        for link in links:
            yield scrapy.Request(link.url)


class SahilOnlineSpider(BaseNewsSpider):
    """
    The sitemap is broken, invalid xml. But we can still extract the urls
    using scrapy's LinkExtractor
    """

    def __init__(self, source, datadir):
        response = requests.get(source['sitemap_url'])
        urls = extract_links(str(response.content))
        urls = list(filter(lambda u: not u.lower().endswith('jpg'), urls))
        self.start_urls = urls
        super().__init__(source, datadir)

    def parse(self, response):
        article = self.parse_article(response)
        if article:
            self.write_article(article)
