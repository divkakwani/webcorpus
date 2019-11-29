"""
Crawls w3newspaper and builds a list of all newspaper URLs
"""

import scrapy

from urllib.parse import urljoin
from ..utils import validate_url


class W3NewsPaperSpider(scrapy.Spider):
    """
    crawls w3newspaper and extracts the news website home urls
    """
    name = 'w3newspaper'
    base_url = 'https://www.w3newspapers.com/india/'

    def __init__(self, languages):
        self.languages = languages
        self.sources = {lang: [] for lang in self.languages}

    def start_requests(self):
        cls = self.__class__
        urls = [urljoin(cls.base_url, lang) for lang in self.languages]
        for url, lang in zip(urls, self.languages):
            yield scrapy.Request(url=url, callback=self.parse,
                                 meta={'lang': lang})

    def parse(self, response):
        lang = response.request.meta['lang']

        # extract urls
        urls = response.css('.bgbul li a::attr(href)').extract()
        urls = list(set(urls))
        urls = list(filter(validate_url, urls))

        # prepare and add sources
        for url in urls:
            self.sources[lang].append(url)
