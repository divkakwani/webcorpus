"""
Crawls w3newspaper and builds a list of all newspaper URLs
"""

import dataclasses
import json
import scrapy

from dataclasses import dataclass
from urllib.parse import urljoin
from utils import lang_code, URL


@dataclass
class Source:
    name: str
    language: str
    home_url: str
    sitemap_url: str


class W3NewsPaperSpider(scrapy.Spider):
    name = 'w3newspaper'
    base_url = 'https://www.w3newspapers.com/india/'
    languages = ['kannada', 'oriya', 'hindi']
    source_urls = {}
    disk_path = None

    def start_requests(self):
        cls = self.__class__
        urls = [urljoin(cls.base_url, lang) for lang in cls.languages]
        for url, lang in zip(urls, cls.languages):
            yield scrapy.Request(url=url, callback=self.parse,
                                 meta={'lang': lang_code(lang)})

    def parse(self, response):
        cls = self.__class__
        urls = response.css('.bgbul li a::attr(href)').extract()
        urls = list(set(urls))
        urls = list(filter(URL.validate, urls))
        lang = response.request.meta['lang']
        cls.source_urls[lang] = urls

    def closed(self, reason):
        cls = self.__class__
        sources = {lang: [] for lang in cls.source_urls}
        for lang in cls.source_urls:
            for url in cls.source_urls[lang]:
                source = Source(name=URL.tld(url), language=lang, home_url=url,
                                sitemap_url=urljoin(url, 'sitemap.xml'))
                sources[lang].append(dataclasses.asdict(source))
        with open(cls.disk_path, 'w') as fp:
            json.dump(sources, fp, indent=4, sort_keys=True)

    def _merge_urls(self, old_source_urls, new_source_urls):
        pass
