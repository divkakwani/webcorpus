
import scrapy
import os

from boilerpipe.extract import Extractor
from utils import URL
from urllib.parse import urljoin


def make_news_crawler(lang, source_url):
    tld = URL.tld(source_url)
    sitemap_url = urljoin(source_url, 'sitemap.xml')
    subclass = type(tld, (NewsSpider,),
                    {"name": tld, "lang": lang, "sitemap_urls": [sitemap_url]})
    return subclass


class NewsSpider(scrapy.spiders.SitemapSpider):
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
        if len(text) < 200:
            return  # Too short for an article

        article_name = URL.page_name(response.url)
        dirpath = os.path.join(cls.disk_path, cls.lang, cls.name)
        os.makedirs(dirpath, exist_ok=True)
        fpath = dirpath + '/' + article_name
        print(fpath)
        with open(fpath, 'w') as fp:
            fp.write(text)
