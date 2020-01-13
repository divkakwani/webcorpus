"""
Copyright © Divyanshu Kakwani 2019, all rights reserved.

Create a sentence file from an article corpus

"""
import json

from tqdm import tqdm
from boilerpipe.extract import Extractor
from datetime import datetime
from ..corpus.io import CatCorpus
from ..language import code2script, in_script


class ArtsProcessor:

    def __init__(self, lang, input_path, output_path):
        self.lang = lang
        self.script = code2script(lang)
        self.input_corpus = CatCorpus(input_path)
        self.output_corpus = CatCorpus(output_path)

    def extract_article(self, html_page):
        extractor = Extractor(extractor='ArticleExtractor',
                              html=html_page['html'])
        body = extractor.getText()
        title = extractor.source.title

        if self.art_ok(body):
            article = {
                'title': title,
                'body': body,
                'source': html_page['source'],
                'url': html_page['url'],
                'timestamp': datetime.now().strftime('%d/%m/%y %H:%M')
            }
            return article
        return None

    def art_ok(self, text, win_sz=250, thres=200):
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

    def gen_dataset(self):
        for cat, iden, data in tqdm(self.input_corpus.files()):
            html_page = json.loads(data)
            article = self.extract_article(html_page)
            if article:
                article_json = json.dumps(article, ensure_ascii=False)
                self.output_corpus.add_file(cat, iden, article_json)
