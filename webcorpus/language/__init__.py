"""
Copyright © Divyanshu Kakwani 2019, all rights reserved
"""

import string
import unicodedata as ud


LC_NAME = {
    'as': 'assamese',
    'bn': 'bengali',
    'bh': 'bihari',
    'en': 'english',
    'gu': 'gujarati',
    'hi': 'hindi',
    'kn': 'kannada',
    'ks': 'kashmiri',
    'ml': 'malayalam',
    'mr': 'marathi',
    'ne': 'nepali',
    'or': 'oriya',
    'pa': 'punjabi',
    'sa': 'sanskrit',
    'sd': 'sindhi',
    'ta': 'tamil',
    'te': 'telugu',
    'ur': 'urdu'
}


LC_SCRIPT = {
    'hi': 'devanagari',
    'kn': 'kannada',
    'mr': 'devanagari',
    'te': 'telugu',
    'ta': 'tamil',
    'gu': 'gujarati',
    'or': 'oriya',
    'bn': 'bengali',
    'ml': 'malayalam',
    'ne': 'devanagari',
    'pa': 'gurmukhi',
    'as': 'bengali',
    'en': 'latin',
    'ur': 'arabic'
}


SCRIPT_DIGITS = {
    'devanagari': '०१२३४५६७८९',
    'gujarati': '૦૧૨૩૪૫૬૭૮૯',
    'telugu': '౦౧౨౩౪౫౬౭౮౯',
    'bengali': '০১২৩৪৫৬৭৮৯',
    'malayalam': '൦൧൨൩൪൫൬൭൮൯',
    'tamil': '௦௧௨௩௪௫௬௭௮௯௰',
    'kannada': '೦೧೨೩೪೫೬೭೮',
    'oriya': '୦୧୨୩୪୫୬୭୮୯',
    'gurmukhi': '੦੧੨੩੪੫੬੭੮੯',
    'latin': '0123456789',
    'urdu': '٠١٢٣٤٥٦٧٨٩٪'
}


def name2code(lang):
    for k, v in LC_NAME.items():
        if v.lower() == lang.lower():
            return k
    return None


def code2script(iso_code):
    iso_code = iso_code.lower()
    for c, s in LC_SCRIPT.items():
        if c == iso_code:
            return s.lower()
    return None


def in_script(char, script_name):
    if char == '।' or char.isspace() or char in string.punctuation:
        return True
    try:
        if script_name not in ud.name(char).lower():
            return False
    except:
        return False
    return True
