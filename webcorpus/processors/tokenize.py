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


class Tokenizer:

    def __init__(self, lang, input_path, output_path):
        self.lang = lang
        self.script = code2script(lang)
        self.input_corpus = FileCorpus(lang, input_path)
        self.output_corpus = FileCorpus(lang, output_path)
        normalizer_factory = IndicNormalizerFactory()
        self.normalizer = normalizer_factory.get_normalizer(self.lang)

    def process_sent(self, sent):
        processed_sent = sent.replace('\n', ' ')

        if self.lang == 'en':
            return ' '.join(word_tokenize(processed_sent))

        processed_sent = self.normalizer.normalize(processed_sent)
        processed_sent = ' '.join(trivial_tokenize(processed_sent, self.lang))

        return processed_sent


    def run(self):
        for sent in tqdm(self.input_corpus.all_instances()):
            processed_sent = self.process_sent(sent)
            self.output_corpus.add_instance(processed_sent)
        self.output_corpus.flush()
