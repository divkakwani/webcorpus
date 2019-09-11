"""
utilities used throughout the code-base
"""

import re
import string
import unicodedata as ud
import tldextract


URL_FMT = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https://
    # domain...
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+"
    r"(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


class URL:
    """
    URL utilities
    """
    @staticmethod
    def validate(url):
        return re.match(URL_FMT, url)

    @staticmethod
    def extract(text):
        return re.findall(r'(https?://[^\s"\\<>]+)', text)

    @staticmethod
    def page_name(url):
        if url[-1] == '/':
            url = url[:-1]
        name = re.search(r'[^\./]*(?!.*/)', url).group(0)
        return name

    @staticmethod
    def tld(url):
        ext = tldextract.extract(url)
        return ext.domain


languages = [
    ('as', 'Assamese'),
    ('bn', 'Bengali'),
    ('bh', 'Bihari languages'),
    ('gu', 'Gujarati'),
    ('hi', 'Hindi'),
    ('kn', 'Kannada'),
    ('ks', 'Kashmiri'),
    ('ml', 'Malayalam'),
    ('mr', 'Marathi'),
    ('ne', 'Nepali'),
    ('or', 'Oriya'),
    ('pa', 'Panjabi; Punjabi'),
    ('sa', 'Sanskrit'),
    ('sd', 'Sindhi'),
    ('ta', 'Tamil'),
    ('te', 'Telugu'),
    ('ur', 'Urdu'),
]


def get_lang_name(code):
    code = code.lower()
    for c, l in languages:
        if c == code:
            return l.lower()
    return None


def lang_code(lang):
    lang = lang.lower()
    for c, l in languages:
        if l.lower() == lang:
            return c
    return None


def is_alphabet(c, lang_name):
    if c.isspace() or c in string.punctuation:
        return True
    try:
        if lang_name not in ud.name(c).lower():
            return False
    except:
        return True
    return True
