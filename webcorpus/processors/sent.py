"""
Copyright © Divyanshu Kakwani 2019, all rights reserved.

Create a sentence file from an article corpus

"""
import re
import json

from tqdm import tqdm
from ..corpus.io import CatCorpus, SentCorpus
from ..language.normalize import IndicNormalizerFactory
from ..language.tokenize import trivial_tokenize
from ..language.sentence_tokenize import sentence_split
from ..language import code2script, SCRIPT_DIGITS, in_script


class SentProcessor:

    def __init__(self, lang, input_path, output_path):
        self.lang = lang
        self.script = code2script(lang)
        self.input_corpus = CatCorpus(input_path)
        self.output_corpus = SentCorpus(output_path)
        normalizer_factory = IndicNormalizerFactory()
        self.normalizer = normalizer_factory.get_normalizer(self.lang)

    def process_sent(self, sent):
        """
        Applies the following pre-processing steps:
            * normalize and tokenize the sentence
            * Replace every number by # token
        """
        newline_removed = sent.replace('\n', ' ')
        normalized = self.normalizer.normalize(newline_removed)
        num_masked = re.sub(r'[0-9]+', '#', normalized)
        native_digits = SCRIPT_DIGITS[self.script]
        num_masked = re.sub(r'[{}]+'.format(native_digits), '#', num_masked)
        spaced = ' '.join(trivial_tokenize(num_masked, self.lang))
        return spaced

    def check_sent(self, sent):
        """
        * Check sentences that contain one or more words not in the
          desired language
        * Check short sentences
        """
        if len(sent) < 10:
            return False
        for c in sent:
            if c != '।' and not in_script(c, self.script):
                return False
        return True

    def gen_dataset(self):
        for payload in tqdm(self.input_corpus.files()):
            article = json.loads(payload)
            content = article['content']
            sents = sentence_split(content, self.lang)
            sents = [self.process_sent(sent) for sent in sents]
            sents = [sent for sent in sents if self.check_sent(sent)]
            self.output_corpus.add_sents(sents)
