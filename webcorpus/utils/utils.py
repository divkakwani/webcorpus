import string
import unicodedata as ud
import re
import tldextract
from urllib.parse import urlparse


############################
# Language utilities
############################

lang_names = [
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
    ('pa', 'Punjabi'),
    ('sa', 'Sanskrit'),
    ('sd', 'Sindhi'),
    ('ta', 'Tamil'),
    ('te', 'Telugu'),
    ('ur', 'Urdu')
]

scripts = [
    ('hi', 'devanagari'),
    ('kn', 'kannada'),
    ('mr', 'devanagari'),
    ('te', 'telugu'),
    ('ta', 'tamil'),
    ('gu', 'gujarati'),
    ('or', 'oriya'),
    ('bn', 'bengali'),
    ('ml', 'malayalam'),
    ('pa', 'gurmukhi'),
    ('as', 'bengali')
]


digits = {
    'devanagari': '०१२३४५६७८९',
    'gujarati': '૦૧૨૩૪૫૬૭૮૯',
    'telugu': '౦౧౨౩౪౫౬౭౮౯',
    'bengali': '০১২৩৪৫৬৭৮৯',
    'malayalam': '൦൧൨൩൪൫൬൭൮൯',
    'tamil': '௦௧௨௩௪௫௬௭௮௯௰',
    'kannada': '೦೧೨೩೪೫೬೭೮',
    'oriya': '୦୧୨୩୪୫୬୭୮୯',
    'gurmukhi': '੦੧੨੩੪੫੬੭੮੯'
}


def get_digits(script):
    return digits.get(script, None)


def langcode2name(iso_code):
    iso_code = iso_code.lower()
    for c, l in lang_names:
        if c == iso_code:
            return l.lower()
    return None


def langname2code(lang):
    lang = lang.lower()
    for c, l in lang_names:
        if l.lower() == lang:
            return c
    return None


def langcode2script(iso_code):
    iso_code = iso_code.lower()
    for c, s in scripts:
        if c == iso_code:
            return s.lower()
    return None


def in_script(c, script_name):
    if c == '।' or c.isspace() or c in string.punctuation:
        return True
    try:
        if script_name not in ud.name(c).lower():
            return False
    except:
        return False
    return True


############################
# URL utilities
############################

def decant_txt(content, lang):
    """
    Extract a window of (500, 700) characters such that all
    the characters belong to that language
    """
    min_win, max_win = 500, 700
    script = langcode2script(lang)
    start = 0
    while start < len(content) - min_win:
        end = start
        while end < len(content) \
                and (in_script(content[end], script) or content[end].isdigit() \
                and end-start < max_win:
            end += 1
        if end - start > min_win:
            return content[start:end]
        start = end + 1
    return None
