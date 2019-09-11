import scrapy
import json
import os
import requests
import tldextract
import sys
import inspect

from boilerpipe.extract import Extractor
from utils import URL, get_lang_name, is_alphabet
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector


def getcrawler(source):
    """
    Dynamically selects spider class based on the source
    """
    # check for a custom spider
    classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    mangled_name = (source['name'] + 'spider').lower()
    for cls_name, clas in classes:
        if mangled_name == cls_name.lower():
            return clas

    # check for the sitemap spider
    if URL.validate(source['sitemap_url']):
        response = requests.get(source['sitemap_url'])
        if response.status_code == 200:
            return NewsSitemapSpider

    # check for recursive spider
    response = requests.get(source['home_url'])
    if response.status_code == 200 or response.status_code == 406:
        return RecursiveSpider

    return None


class BaseNewsSpider(scrapy.Spider):

    custom_settings = {
        'DOWNLOAD_DELAY': 0.2,
        # 'LOG_ENABLED': False,
        'CONCURRENT_REQUESTS': 32,
        'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': None,
    }

    def __init__(self, source):
        self.lang = source['language']
        self.lang_name = get_lang_name(self.lang)
        self.name = source['name']

        self.disk_path = os.path.join('./data/raw', self.lang, self.name)
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
                'name': URL.page_name(response.url),
                'content': text,
                'source': response.request.url
            }
            return article
        return None

    def _is_article(self, text, win_sz=300, thres=260):
        """
        It performs two tests on the text to determine if is a valid news
        article or not:
        1. Has length greater than `win_sz`
        2. Contains a continuous subtext of atleast length `win_sz` having
           atleast `thres` characters in the required language
        """
        txt_sz = len(text)
        if txt_sz < win_sz:
            return False

        chr_valid = [is_alphabet(c, self.lang_name) for c in text]
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

    def __init__(self, source):
        super().__init__(source)
        self.sitemap_urls = [source['sitemap_url']]

    def parse(self, response):
        article = self.parse_article(response)
        if article:
            self.write_article(article)


class RecursiveSpider(BaseNewsSpider):

    def __init__(self, source):
        self.start_urls = [source['home_url']]
        self.link_extractor = LinkExtractor()
        super().__init__(source)

    def parse(self, response):
        article = self.parse_article(response)
        if article:
            self.write_article(article)

        links = self.link_extractor.extract_links(response)
        for link in links:
            yield scrapy.Request(link.url)


class SanjevaniSpider(RecursiveSpider):

    def extract_article_content(self, html):
        sel = Selector(text=html)
        text = ''
        for node in sel.css('.entry-content *::text'):
            text = text + '\n' + node.extract()
        return text


class BalkaniNewsSpider(NewsSitemapSpider):

    def __init__(self, source):
        super().__init__(source)
        self.link_extractor = LinkExtractor()

    def parse(self, response):
        article = self.parse_article(response)
        if article:
            self.write_article(article)

        links = self.link_extractor.extract_links(response)
        for link in links:
            yield scrapy.Request(link.url)


class SahilOnlineSpider(BaseNewsSpider):

    def __init__(self, source):
        response = requests.get(source['sitemap_url'])
        urls = URL.extract(str(response.content))
        urls = list(filter(lambda u: not u.lower().endswith('jpg'), urls))
        self.start_urls = urls
        super().__init__(source)

    def parse(self, response):
        article = self.parse_article(response)
        if article:
            self.write_article(article)
