
import scrapy
import requests
import re

from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from webcorpus.crawlers.news import BaseNewsSpider
from webcorpus.crawlers.news import RecursiveSpider, SitemapSpider


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

        links = self.link_extractor.extract_links(response)
        for link in links:
            yield scrapy.Request(link.url)


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
