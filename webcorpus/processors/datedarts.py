"""
Copyright © Divyanshu Kakwani 2021, all rights reserved.

Create a article corpus from html corpus

"""
import json
import os
import multiprocessing as mp

from tqdm import tqdm
from hashlib import sha1
from htmldate.cli import examine
from datetime import datetime
from ..corpus import DirCorpus, NewsCorpus
from ..language import code2script, in_script
from ..language.sentence_tokenize import sentence_split
from nltk.tokenize import sent_tokenize, word_tokenize


class DatedCorpus(DirCorpus):

    def get_path(self, instance):
        date = datetime.strptime(instance['publish_date'],'%Y-%m-%d')
        url = instance['url']
        fname = sha1(url.encode('utf-8')).hexdigest()
        return os.path.join(date.year, date.month, date.day, fname)


class DatedProcessor:

    def __init__(self, lang, input_path, output_path):
        self.lang = lang
        self.script = code2script(lang)
        self.input_corpus = NewsCorpus(lang, input_path)
        self.output_corpus = DatedCorpus(lang, output_path)

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

    def check_sent(self, sent):
        """
        * Check sentences that contain one or more words not in the
          desired language
        * Check short sentences
        """
        if len(sent) < 10:
            return False
        cval = map(lambda c: in_script(c, self.script) or c.isdigit(), sent)
        if sum(cval) >= 0.9*len(sent):
            return True
        return False


    def process_item(self, html_page):
        try:
            publish_date = examine(html_page['html'])
            from boilerpipe.extract import Extractor
            extractor = Extractor(extractor='ArticleExtractor',
                                  html=html_page['html'])
            body = str(extractor.getText())
            title = str(extractor.source.getTitle())
            art = {
                'title': title,
                'body': body,
                'source': html_page['source'],
                'url': html_page['url'],
                'crawl_date': html_page['timestamp'],
                'publish_date': publish_date,
                'article_id': sha1(html_page['url'].encode('utf-8')).hexdigest(),
                'sentences': []
            }
            if self.art_ok(art['body']):
                content = art['body']
                content = content.replace(u'\xa0', u' ')
                content = content.replace('\\n', '\n')
                sents = []
                if self.lang == 'en':
                    sents = sent_tokenize(content)
                else:
                    for para in content.split('\n'):
                        sents += sentence_split(para, self.lang)
                    sents = [sent for sent in sents if self.check_sent(sent)]
                art['sentences'] = sents
                if len(sents) > 3:
                    self.output_corpus.add_instance(art)
        except Exception as e:
            pass

    def run(self):
        proc_pool = mp.Pool(mp.cpu_count())
        for _ in tqdm(proc_pool.imap_unordered(self.process_item, self.input_corpus.all_instances(), 32)):
            pass
        proc_pool.terminate()
        proc_pool.join()
