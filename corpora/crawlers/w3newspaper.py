"""
Crawls w3newspaper and builds a list of all newspaper URLs
"""

import scrapy

from urllib.parse import urljoin
from ..utils import langname2code, url_validate, url_tld
from ..sources import SourceList


class W3NewsPaperSpider(scrapy.Spider):
    name = 'w3newspaper'
    base_url = 'https://www.w3newspapers.com/india/'

    def __init__(self):
        self.languages = ['kannada', 'oriya', 'hindi', 'punjabi',
                          'assamese', 'punjabi', 'tamil', 'telugu',
                          'gujarati']
        self.source_lists = {}
        for lang in self.languages:
            langcode = langname2code(lang)
            self.source_lists[langcode] = SourceList(langcode)

    def start_requests(self):
        cls = self.__class__
        urls = [urljoin(cls.base_url, lang) for lang in self.languages]
        for url, lang in zip(urls, self.languages):
            yield scrapy.Request(url=url, callback=self.parse,
                                 meta={'lang': langname2code(lang)})

    def parse(self, response):
        lang = response.request.meta['lang']

        # extract urls
        urls = response.css('.bgbul li a::attr(href)').extract()
        urls = list(set(urls))
        urls = list(filter(url_validate, urls))

        # prepare and add sources
        for url in urls:
            name = url_tld(url)
            sitemap_url = urljoin(url, 'sitemap.xml')
            source = {'name': name, 'language': lang, 'home_url': url,
                      'sitemap_url': sitemap_url}
            self.source_lists[lang].add_source(source)
