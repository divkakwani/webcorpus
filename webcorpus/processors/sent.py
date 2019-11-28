
from tqdm import tqdm






def gen_dataset(*args, **kwargs):
    """
    Applies the following pre-processing steps:
        * Remove sentences that contain one or more words not in the
          desired language
        * Remove short sentences
        * Treat punctuation marks as words. Insert spaces around them
        * Lowercase all the letters (in case of English)
        * Replace every number by # token
    """

    def __init__(self, ip_corpus_path, lang, corpus_fmt, op_corpus_path):
        self.lang = lang
        self.script = langcode2script(lang)
        self.corpus_path = ip_corpus_path
        self.corpus_reader = CorpusReader(ip_corpus_path, lang, corpus_fmt)
        normalizer_factory = indic_normalize.IndicNormalizerFactory()
        self.normalizer = normalizer_factory.get_normalizer(lang)
        # self.stop_sents = self._stop_sents()
        self.stop_sents = set()
        self.corpus_writer = CorpusWriter(op_corpus_path)

    def _process_sent(self, sent):
        newline_removed = sent.replace('\n', ' ')
        normalized = self.normalizer.normalize(newline_removed)
        num_masked = re.sub(r'[0-9]+', '#', normalized)
        native_digits = get_digits(self.script)
        num_masked = re.sub(r'[{}]+'.format(native_digits), '#', num_masked)
        spaced = ' '.join(indic_tokenize.trivial_tokenize(num_masked,
                                                          self.lang))
        return spaced

    def process(self):
        for sent in tqdm(self.corpus_reader.sents()):
            sent = self._process_sent(sent)
            if self._sent_filter(sent):
                self.corpus_writer.add_sents(sent)

    def _sent_filter(self, sent):
        if len(sent) < 10:
            return False
        for c in sent:
            if c != '।' and not in_script(c, self.script):
                return False
        return True
