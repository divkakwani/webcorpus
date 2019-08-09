import scrapy
import os
import re
import json
import tldextract

from scrapy.crawler import CrawlerProcess
from urllib.parse import urljoin
from boilerpipe.extract import Extractor


def dom(url):
    ext = tldextract.extract(url)
    return ext.domain


def get_news_urls():
    with open("./data/news_sources.json") as fp:
        return json.load(fp)


def extract_article_name(url):
    return re.search(r'[^\./]*(?!.*/)', url).group(0)


def make_news_class(lang, url):
    domain = dom(url)
    subclass = type(domain, (NewsSpider,),
                    {"name": domain, "lang": lang, "sitemap_urls": [url]})
    return subclass


class NewsSpider(scrapy.spiders.SitemapSpider):
    name = "newsspider"

    custom_settings = {
        'DOWNLOAD_DELAY': 0.25,
    }

    def parse(self, response):
        # Use scrapy items?
        extractor = Extractor(extractor="ArticleExtractor", html=response.body)
        text = extractor.getText()
        if len(text) > 200:
            article_name = extract_article_name(response.url)
            lang, news_id = self.__class__.lang, self.__class__.name
            dirpath = './data/processed/{}/{}/'.format(lang, news_id)
            os.makedirs(dirpath, exist_ok=True)
            fpath = dirpath + article_name
            with open(fpath, 'w') as fp:
                fp.write(text)


if __name__ == "__main__":
    all_urls = get_news_urls()
    all_urls = [(k, v) for k in all_urls for v in all_urls[k]]
    sitemap_urls = [(l, urljoin(u, "sitemap.xml")) for l, u in all_urls]

    process = CrawlerProcess()
    for lang, url in sitemap_urls:
        process.crawl(make_news_class(lang, url))
    process.start()  # block until all crawling jobs are finished

