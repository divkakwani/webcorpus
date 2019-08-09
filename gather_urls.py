"""
Gathers newspaper URLs from w3newspapers
"""

import scrapy
import os
import json
import re

from urllib.parse import urljoin


URL_FMT = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https://
    # domain...
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+"
    r"(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


class W3NewsPaperSpider(scrapy.Spider):
    name = "w3newspaper"

    def __init__(self):
        self.langs = ["kannada", "oriya", "hindi"]
        self.save_fpath = "./data/news_sources.json"
        try:
            with open(self.save_fpath, "r") as fp:
                self.all_urls = json.load(fp)
        except (IOError, ValueError):
            self.all_urls = {}

    def start_requests(self):
        base_url = "https://www.w3newspapers.com/india/"
        urls = [urljoin(base_url, l) for l in self.langs]
        for url, lang in zip(urls, self.langs):
            yield scrapy.Request(url=url, callback=self.parse, meta={"lang": lang})

    def parse(self, response):
        urls = response.css(".bgbul li a::attr(href)").extract()
        urls = list(set(urls))
        urls = list(filter(lambda x: re.match(URL_FMT, x) is not None, urls))
        lang = response.request.meta["lang"]
        self.all_urls[lang] = urls

    def closed(self, reason):
        with open(self.save_fpath, "w") as f:
            json.dump(self.all_urls, f, indent=4, sort_keys=True)
