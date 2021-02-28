"""
Copyright © Divyanshu Kakwani 2019, all rights reserved.

Create a article file corpus from article dir corpus
"""
import json
import string
import regex

from nltk.tokenize import sent_tokenize, word_tokenize
from tqdm import tqdm
from ..corpus import FileCorpus, NewsCorpus
from ..language.sentence_tokenize import sentence_split
from ..language import code2script, in_script


class ArtsProcessor:

    def __init__(self, lang, input_path, output_path, meta_file):
        self.lang = lang
        self.script = code2script(lang)
        self.input_corpus = NewsCorpus(lang, input_path)
        self.arts_file = FileCorpus(lang, output_path)
        self.meta_file = FileCorpus(lang, meta_file)

    def _strip_txt(self, txt):
        txt = txt.strip()
        neg_letter = string.digits + string.ascii_letters + string.punctuation + string.whitespace
        s, e = 0, len(txt) - 1
        if self.lang != 'en':
            while s < len(txt) and txt[s] in neg_letter:
                s += 1
            while e >= 0 and txt[e] in neg_letter:
                e -= 1
        return txt[s:e+1]

    def clean_article(self, art):
        # remove unneccesary fields in the title like newspaper name etc.
        titles = art['title'].split('|')
        art['title'] = max(titles, key=len)

        # remove title from the body content
        # boilerpipe tends to include the title also in the body content
        pattern = regex.compile('({}){{e<=5}}'.format(regex.escape(art['title'])))
        match = pattern.search(art['body'])
        if match:
            end_idx = match.span()[1]
            art['body'] = art['body'][end_idx:]
            art['body'] = self._strip_txt(art['body'])
            art = self.clean_article(art)
        
        art['title'] = self._strip_txt(art['title'])
        art['body'] = self._strip_txt(art['body'])

        return art

    def run(self):
        """
        Input file format:
        (1) One sentence per line. These should ideally be actual sentences, not
        entire paragraphs or arbitrary spans of text. (Because we use the
        sentence boundaries for the "next sentence prediction" task).
        (2) Blank lines between documents. Document boundaries are needed so
        that the "next sentence prediction" task doesn't span between documents.
        """
        for article in tqdm(self.input_corpus.all_instances()):
            article = self.clean_article(article)
            content = article['body']

            if len(content) < 128:
                continue

            sents = []
            if self.lang == 'en':
                sents = sent_tokenize(content)
            else:
                for para in content.split('\n'):
                    sents += sentence_split(para, self.lang)

            self.meta_file.add_instance(article['url'])
            for sent in sents:
                self.arts_file.add_instance(sent)
            self.arts_file.add('\n')
