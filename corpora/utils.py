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
    if c.isspace() or c in string.punctuation:
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

fmt = re.compile(
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


def url_validate(url):
    return re.match(fmt, url)


def extract_links(text):
    return re.findall(r'(https?://[^\s"\\<>]+)', text)


def page_name(url):
    if url[-1] == '/':
        url = url[:-1]
    name = re.search(r'[^\./]*(?!.*/)', url).group(0)
    return name

def flatten_url_path(url):
    """Given an URL, returns the flattened path from the URL.
    
    Examples:
        >>> flatten_url_path('http://abc.com/news.php;national?article=123#fragment')
        news-national--article=123
    
    Todo:
        - Implement using regex if slow.
    """
    
    url = urlparse(url)
    path = url.path[1:].rsplit('.', 1)[0]
    if url.params:
        path += '-' + url.params
    if url.query:
        path += '--' + url.query
    return path.replace('/', '-')[:255] if path else url.hostname

def url_tld(url):
    ext = tldextract.extract(url)
    return ext.domain
