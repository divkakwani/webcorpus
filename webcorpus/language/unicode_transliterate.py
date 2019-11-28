"""
Taken from https://github.com/anoopkunchukuttan/indic_nlp_library
"""

from . import langinfo
from . import itrans_transliterator
from .sinhala_transliterator import (
    SinhalaDevanagariTransliterator as sdt,
)


class UnicodeIndicTransliterator(object):
    """
    Base class for rule-based transliteration among Indian languages.

    Script pair specific transliterators should derive from this class
    and override the transliterate() method.  They can call the super
    class 'transliterate()' method to avail of the common transliteration
    """

    @staticmethod
    def _correct_tamil_mapping(offset):
        # handle missing unaspirated and voiced plosives in Tamil script
        # replace by unvoiced, unaspirated plosives

        # for first 4 consonant rows of varnamala
        # exception: ja has a mapping in Tamil
        if (
            offset >= 0x15
            and offset <= 0x28
            and offset != 0x1C
            and not ((offset - 0x15) % 5 == 0 or (offset - 0x15) % 5 == 4)
        ):
            subst_char = (offset - 0x15) // 5
            offset = 0x15 + 5 * subst_char

        # for 5th consonant row of varnamala
        if offset in [0x2B, 0x2C, 0x2D]:
            offset = 0x2A

        # 'sh' becomes 'Sh'
        if offset == 0x36:
            offset = 0x37

        return offset

    @staticmethod
    def transliterate(text, lang1_code, lang2_code):
        """
        convert the source language script (lang1) to target language
        script (lang2)

        text: text to transliterate
        lang1_code: language 1 code
        lang1_code: language 2 code
        """
        if (
            lang1_code in langinfo.SCRIPT_RANGES
            and lang2_code in langinfo.SCRIPT_RANGES
        ):

            # if Sinhala is source, do a mapping to Devanagari first
            if lang1_code == "si":
                text = sdt.sinhala_to_devanagari(text)
                lang1_code = "hi"

            # if Sinhala is target, make Devanagiri the intermediate target
            org_lang2_code = ""
            if lang2_code == "si":
                lang2_code = "hi"
                org_lang2_code = "si"

            trans_lit_text = []
            for c in text:
                newc = c
                offset = ord(c) - langinfo.SCRIPT_RANGES[lang1_code][0]
                if (
                    offset >= langinfo.COORDINATED_RANGE_START_INCLUSIVE
                    and offset <= langinfo.COORDINATED_RANGE_END_INCLUSIVE
                ):
                    if lang2_code == "ta":
                        # tamil exceptions
                        offset = UnicodeIndicTransliterator\
                            ._correct_tamil_mapping(offset)
                    newc = chr(langinfo.SCRIPT_RANGES[lang2_code][0] + offset)

                trans_lit_text.append(newc)

            # if Sinhala is source, do a mapping to Devanagari first
            if org_lang2_code == "si":
                return sdt.devanagari_to_sinhala("".join(trans_lit_text))

            return "".join(trans_lit_text)
        else:
            return text


class ItransTransliterator(object):
    """
    Transliterator between Indian scripts and ITRANS
    """

    @staticmethod
    def to_itrans(text, lang_code):
        if lang_code in langinfo.SCRIPT_RANGES:
            if lang_code == "ml":
                # Change from chillus characters to corresponding
                # consonant+halant
                text = text.replace("\u0d7a", "\u0d23\u0d4d")
                text = text.replace("\u0d7b", "\u0d28\u0d4d")
                text = text.replace("\u0d7c", "\u0d30\u0d4d")
                text = text.replace("\u0d7d", "\u0d32\u0d4d")
                text = text.replace("\u0d7e", "\u0d33\u0d4d")
                text = text.replace("\u0d7f", "\u0d15\u0d4d")

            devnag = UnicodeIndicTransliterator\
                .transliterate(text, lang_code, "hi")

            itrans = itrans_transliterator.transliterate(
                devnag.encode("utf-8"),
                "devanagari",
                "itrans",
                {
                    "outputASCIIEncoded": False,
                    "handleUnrecognised": itrans_transliterator.UNRECOGNISED_ECHO,
                },
            )
            return itrans.decode("utf-8")
        else:
            return text

    @staticmethod
    def from_itrans(text, lang_code):
        if lang_code in langinfo.SCRIPT_RANGES:
            devnag_text = itrans_transliterator.transliterate(
                text.encode("utf-8"),
                "itrans",
                "devanagari",
                {
                    "outputASCIIEncoded": False,
                    "handleUnrecognised": itrans_transliterator.UNRECOGNISED_ECHO,
                },
            )

            lang_text = UnicodeIndicTransliterator.transliterate(
                devnag_text.decode("utf-8"), "hi", lang_code
            )

            return lang_text
        else:
            return text
