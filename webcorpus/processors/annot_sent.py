"""
Copyright © Divyanshu Kakwani 2019, all rights reserved.

Create a sentence file from an article corpus

"""
import json
import nltk

from nltk.tokenize import sent_tokenize, word_tokenize
from tqdm import tqdm
from ..corpus.io import CatCorpus, SentCorpus
from ..language.normalize import IndicNormalizerFactory
from ..language.tokenize import trivial_tokenize
from ..language.sentence_tokenize import sentence_split
from ..language import code2script, in_script


# nltk.download('punkt')


class SentProcessor:

    def __init__(self, lang, input_path, output_path):
        self.lang = lang
        self.script = code2script(lang)
        self.input_corpus = SentCorpus(input_path)
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
        if self.lang == 'en':
            return ' '.join(word_tokenize(newline_removed))

        normalized = self.normalizer.normalize(newline_removed)
        # num_masked = re.sub(r'[0-9]+', '#', normalized)
        # native_digits = SCRIPT_DIGITS[self.script]
        # num_masked = re.sub(r'[{}]+'.format(native_digits), '#', num_masked)
        spaced = ' '.join(trivial_tokenize(normalized, self.lang))
        return spaced

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

    def gen_dataset(self):
        for content in tqdm(self.input_corpus.sents()):
            if self.lang == 'en':
                sents = sent_tokenize(content)
            else:
                sents = sentence_split(content, self.lang)
            sents = [self.process_sent(sent) for sent in sents]
            sents = [sent for sent in sents if self.check_sent(sent)]
            self.output_corpus.add_sents(sents)
