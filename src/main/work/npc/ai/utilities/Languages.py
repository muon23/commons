import re
import string

import nltk
from typing import Tuple, Generator
from zhon import zhuyin, hanzi

nltk.download('punkt')


class Languages:
    _quoteStart = r"\[({'\"«‹“‘（［｛｟｢〈《「『【"
    _quoteEnd = r"])}'\"»›”’）］｝｠｣〉》」』】"

    _punctuation = re.compile(f"[{_quoteEnd}{_quoteStart}{hanzi.punctuation}{string.punctuation}\n ]")
    _ideography = re.compile(f"[{hanzi.characters}{hanzi.radicals}{zhuyin.characters}]")
    _startQuote = re.compile(f"[{_quoteStart}]")
    _number = re.compile("[0-9]")
    _alphabetical = re.compile(r"\w")

    @classmethod
    def isPunctuation(cls, char: str) -> bool:
        return char and cls._punctuation.match(char) is not None

    @classmethod
    def isIdeography(cls, char: str) -> bool:
        return char and cls._ideography.match(char) is not None

    @classmethod
    def isAlphabetical(cls, char: str) -> bool:
        return char and cls._alphabetical.match(char) is not None

    @classmethod
    def isNumber(cls, char: str) -> bool:
        return char and cls._number.match(char) is not None

    @classmethod
    def isStartQuote(cls, char: str) -> bool:
        return char and cls._startQuote.match(char) is not None

    @classmethod
    def separateIdeograph(cls, text: str) -> Tuple[str, str]:
        if text is None:
            return "", ""

        ideographic = ""
        alphabetical = ""

        last = None
        pending = ""

        for i in range(len(text)):
            char = text[i]
            if cls.isPunctuation(char) or cls.isNumber(char):
                if cls.isStartQuote(char) or not last:
                    pending += char
                elif last == "i":
                    ideographic += char
                else:
                    alphabetical += char
            elif cls.isIdeography(char):
                ideographic += pending + char
                pending = ""
                last = "i"
            else:
                alphabetical += pending + char
                pending = ""
                last = "a"

        return ideographic, alphabetical

    _englishStops = ".?!"
    _englishEndQuotes = "\"'”“"
    _stops = hanzi.stops + _englishStops
    _hanziSentence = re.compile(f"[^{_stops}]+[{_stops}]")
    _englishSentence = re.compile(f"([^{_englishStops}]+[{_englishStops}]+[{_englishEndQuotes}]?)(\\s+|$)")
    _spaces = re.compile(r"\s+")
    _leadingBlanks = re.compile(r"^[\t\n ]+")
    _trailingBlanks = re.compile(r"[\t\n ]+$")
    _blanks = " \n\t\r"

    @staticmethod
    def _fixText(text):
        # Fixing spaces
        text.strip()
        text = Languages._spaces.sub(" ", text)
        text = Languages._leadingBlanks.sub("", text)
        text = Languages._trailingBlanks.sub("", text)

        # If not ended with a period, add one
        if text[-1:] not in Languages._stops + Languages._englishEndQuotes:
            text += "."

        return text

    _abbreviations = [
        "No", "Mr", "Mrs", "Ms", "Messrs", "Mmes", "Dr", "Prof", "Rev", "Sen", "Hon", "St", "MD", "PhD",
        "Mt", "Jr", "Sr",
    ]
    _dot = "%%PERIOD%%"

    @staticmethod
    def _replaceDots(text):
        result = text
        for ab in Languages._abbreviations:
            result = result.replace(ab + ". ", f"{ab}{Languages._dot} ")

        result = re.sub(
            f"[^{Languages._englishStops}]([{Languages._englishStops}])((?!(\\s|[\n]|$))|(?={Languages._englishEndQuotes}))",
            lambda matched: matched.group(0).replace(".", Languages._dot),
            result
        )
        return result

    @staticmethod
    def _recoverDots(text):
        result = text.replace(Languages._dot, ".")
        return result

    @staticmethod
    def hanziSentences(text):
        text = Languages._fixText(text)
        text = Languages._replaceDots(text)
        result = Languages._hanziSentence.findall(text)
        return [Languages._recoverDots(s) for s in result]

    @staticmethod
    def englishSentences(text):
        text = Languages._fixText(text)
        text = Languages._replaceDots(text)
        # return nltk.tokenize.sent_tokenize(text)
        # My rule is better than NLTK's
        result = [s[0] for s in Languages._englishSentence.findall(text)]
        return [Languages._recoverDots(s) for s in result]

    @staticmethod
    def sentences(text: str) -> Generator[Tuple[int, str], None, None]:
        sentence = ""
        sentenceBegin = 0
        i = 0

        while i < len(text):

            if sentence == "":
                # If we are starting to look for a new sentence, skipping leading blanks
                while i < len(text) and text[i] in Languages._blanks:
                    i += 1

                if i == len(text):   # End of text
                    break

                sentenceBegin = i

            sentence += text[i]

            if text[i] in Languages._stops:
                # We see a . ! ? or other potential sentence stops.  Let's see if it is really a sentence

                if i < len(text)-1 and text[i+1] in Languages._quoteEnd:
                    # An end quote after sentence stop.  Include all the end quotes afterward into the sentence.
                    k = i+2
                    while k < len(text) and text[k] in Languages._quoteEnd:
                        k += 1
                    sentence += text[i+1:k]
                    yield sentenceBegin, sentence
                    sentence = ""

                    if k == len(text): # End of text
                        break

                    i = k-1

                elif i < len(text)-1 and text[i+1] in Languages._blanks:
                    # A blank after stop, potentially a sentence unless it is a abbreviation of titles (Mr., Dr.) or a
                    # numbered item (1. 2. 3.).

                    # Some of the exceptions below could actually be the end of a sentence, but those conditions
                    # happens rarer than when those occurring in the middle of a sentence.

                    # Go backward to find the last space
                    k = i - 1
                    while k > sentenceBegin and text[k] not in Languages._blanks:
                        k -= 1
                    lastWord = text[k+1:i]

                    if lastWord in Languages._abbreviations:  # Mr./Dr./Mt., not the end of a sentence
                        pass

                    elif re.match(r"\d+", lastWord):  # An item of a numbered list
                        pass

                    elif re.match(r"[.]+", lastWord):  # It is like ...
                        pass

                    elif re.match(r"(\w+[.])+\w+", lastWord):  # Abbreviation like A.B.C., Ph.D.
                        pass

                    else:
                        yield sentenceBegin, sentence
                        sentence = ""

                elif text[i] in hanzi.stops:
                    # Chinese language stops doesn't need a blank behind
                    yield sentenceBegin, sentence
                    sentence = ""

            i += 1

        if sentence != "":
            # End of the text reached and there are still things left over in the sentence
            yield sentenceBegin, sentence

    @staticmethod
    def implySentences(text):
        text = Languages._fixText(text)

        str = ""
        lastCharType = ""

        for char in text:
            if char == '\n':
                if lastCharType == "a":
                    str += ". "
                elif lastCharType == "i":
                    str += "。"
                elif lastCharType == "p":
                    str += " "
                lastCharType = ""
            else:
                str += char

                if Languages._punctuation.match(char):
                    lastCharType = "p"
                elif Languages._ideography.match(char):
                    lastCharType = "i"
                elif Languages._alphabetical.match(char):
                    lastCharType = "a"
                else:
                    lastCharType = ""

        return str

    @staticmethod
    def _typeName(language):
        if language == 1:
            return "English"
        elif language == 2:
            return "Chinese (traditional)"
        elif language == 3:
            return "Chinese (simplified)"
        else:
            return "Unknown"
