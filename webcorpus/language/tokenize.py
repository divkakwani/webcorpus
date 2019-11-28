"""
Taken from https://github.com/anoopkunchukuttan/indic_nlp_library
"""

import string
import re


triv_tokenizer_indic_pat = re.compile(
    r"([" + string.punctuation + r"\u0964\u0965" + r"])"
)
triv_tokenizer_urdu_pat = re.compile(
    r"(["
    + string.punctuation
    + r"\u0609\u060A\u060C\u061E\u066A\u066B\u066C\u066D\u06D4"
    + r"])"
)


# date, numbers, section/article numbering
pat_num_seq = re.compile(r"([0-9]+ [,.:/] )+[0-9]+")


def trivial_tokenize_indic(s):
    """
    A trivial tokenizer which just tokenizes on the punctuation boundaries.
    This also includes punctuations for the Indian language scripts - the
    purna virama and the deergha virama
    returns a list of tokens
    """
    tok_str = triv_tokenizer_indic_pat.sub(r" \1 ", s.replace("\t", " "))
    #     return re.sub(r'[ ]+',' ',tok_str).strip(' ').split(' ')

    s = re.sub(r"[ ]+", " ", tok_str).strip(" ")

    # do not tokenize numbers and dates
    new_s = ""
    prev = 0
    for m in pat_num_seq.finditer(s):
        start = m.start()
        end = m.end()
        if start > prev:
            new_s = new_s + s[prev:start]
            new_s = new_s + s[start:end].replace(" ", "")
            prev = end

    new_s = new_s + s[prev:]
    s = new_s

    return s.split(" ")


def trivial_tokenize_urdu(s):
    """
    A trivial tokenizer which just tokenizes on the punctuation boundaries.
    This also includes punctuations for the Urdu script. These punctuations
    characters were identified from the Unicode database for Arabic script by
    looking for punctuation symbols.
    returns a list of tokens
    """
    tok_str = triv_tokenizer_urdu_pat.sub(r" \1 ", s.replace("\t", " "))
    return re.sub(r"[ ]+", " ", tok_str).strip(" ").split(" ")


def trivial_tokenize(s, lang="hi"):
    """
    Trivial tokenizer for languages in the Indian sub-continent
    """
    if lang == "ur":
        return trivial_tokenize_urdu(s)
    else:
        return trivial_tokenize_indic(s)
