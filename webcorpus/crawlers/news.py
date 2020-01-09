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
        self.arts_collected = 0

        os.makedirs(self.arts_path, exist_ok=True)
        os.makedirs(self.html_path, exist_ok=True)

        parts = tldextract.extract(self.home_url)
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
        if self._is_article(content['body']):
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
        if self.arts_collected % 100 == 0:
            event = {'type': 'arts-count', 'lang': self.lang,
                     'source': self.name, 'count': self.arts_collected}
            self.remote_channel.send_event(event)
        self.arts_corpus.add_file(article['source'], article['url'], dump)

    def write_html(self, response):
        html = response.body.decode(response.encoding)
        self.html_corpus.add_file(self.name, response.request.url, html)

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
        article = self.parse_article(response)
        if article:
            self.write_article(article)
        self.write_html(response)


class RecursiveSpider(BaseNewsSpider):

    name = 'recursive-spider'

    def __init__(self, *args, **kwargs):
        self.start_urls = [kwargs['home_url']]
        self.link_extractor = LinkExtractor()
        super().__init__(*args, **kwargs)

    def parse(self, response):
        article = self.parse_article(response)
        if article:
            self.write_article(article)
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
