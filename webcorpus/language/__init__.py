"""
Copyright © Divyanshu Kakwani 2019, all rights reserved
"""


LC_NAME = {
    'as': 'assamese',
    'bn': 'bengali',
    'bh': 'bihari',
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
    'pa': 'gurmukhi',
    'as': 'bengali'
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
    'gurmukhi': '੦੧੨੩੪੫੬੭੮੯'
}


def name2code(lang):
    for k, v in LC_NAME.items():
        if v.lower() == lang.lower():
            return k
    return None
