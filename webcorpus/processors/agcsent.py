"""
Copyright © Divyanshu Kakwani 2021, all rights reserved.

Create a sentence file from an article corpus

"""
import json
import sys
import nltk

from nltk.tokenize import sent_tokenize, word_tokenize
from tqdm import tqdm
from ..corpus import NewsCorpus, FileCorpus
from ..language.normalize import IndicNormalizerFactory
from ..language.tokenize import trivial_tokenize
from ..language.sentence_tokenize import sentence_split
from ..language import code2script, in_script


# nltk.download('punkt')


class AgcSent:

    def __init__(self, lang, input_path, output_path):
        self.lang = lang
        self.script = code2script(lang)
        self.input_corpus = FileCorpus(lang, input_path, encoding='csv', header=True)
        self.output_corpus = FileCorpus(lang, output_path)
        normalizer_factory = IndicNormalizerFactory()
        self.normalizer = normalizer_factory.get_normalizer(self.lang)

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

    def run(self):
        for _, content in tqdm(self.input_corpus.all_instances()):
            content = content.replace(u'\xa0', u' ')
            content = content.replace('\\n', '\n')
            sents = []
            if self.lang == 'en':
                sents = sent_tokenize(content)
            else:
                for para in content.split('\n'):
                    sents += sentence_split(para, self.lang)
            sents = [sent for sent in sents if self.check_sent(sent)]
            for sent in sents:
                self.output_corpus.add_instance(sent)
        self.output_corpus.flush()
