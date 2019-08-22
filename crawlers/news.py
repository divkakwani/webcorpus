
import scrapy
import os
import requests

from boilerpipe.extract import Extractor
from utils import URL
from scrapy.linkextractors import LinkExtractor


def make_news_crawler(lang, source):
    use_sitemap = False
    request = requests.get(source['sitemap_url'])
    if request.status_code == 200:
        use_sitemap = True
    if use_sitemap:
        subclass = type(source['name'], (NewsSitemapSpider,),
                        {"name": source['name'], 'lang': lang,
                         "sitemap_urls": [source['sitemap_url']]})
    else:
        subclass = type(source['name'], (NewsHomeSpider,),
                        {"name": source['name'], "lang": lang,
                         "start_urls": [source['home_url']]})
    return subclass


class NewsSpider:
    name = "newsspider"
    disk_path = './data/raw'

    custom_settings = {
        'DOWNLOAD_DELAY': 0.25,
    }

    def parse(self, response):
        cls = self.__class__
        # Use scrapy items?
        extractor = Extractor(extractor="ArticleExtractor", html=response.body)
        text = extractor.getText()

        if not self._articleness_test(text):
            return

        article_name = URL.page_name(response.url)
        dirpath = os.path.join(cls.disk_path, cls.lang, cls.name)
        os.makedirs(dirpath, exist_ok=True)
        fpath = dirpath + '/' + article_name
        with open(fpath, 'w') as fp:
            fp.write(text)

    def _articleness_test(self, text):
        if len(text) < 100:
            return False
        return True


class NewsSitemapSpider(NewsSpider, scrapy.spiders.SitemapSpider):
    pass


class NewsHomeSpider(NewsSpider, scrapy.Spider):

    link_extractor = LinkExtractor()

    def parse(self, response):
        cls = self.__class__
        # Use scrapy items?
        extractor = Extractor(extractor="ArticleExtractor", html=response.body)
        text = extractor.getText()

        if not self._articleness_test(text):
            return

        article_name = URL.page_name(response.url)
        dirpath = os.path.join(cls.disk_path, cls.lang, cls.name)
        os.makedirs(dirpath, exist_ok=True)
        fpath = dirpath + '/' + article_name
        with open(fpath, 'w') as fp:
            fp.write(text)

        links = cls.link_extractor.extract_links(response)
        print(list(links))
        for link in links:
            yield scrapy.Request(link.url)
