import re
import string

import nltk
from zhon import zhuyin, hanzi

nltk.download('punkt')


class Languages:
    _quoteStart = r"\[({'\"«‹“‘（［｛｟｢〈《「『【"
    _quoteEnd = r"\])}'\"»›”’）］｝｠｣〉》」』】"

    _punctuation = re.compile(f"[{_quoteEnd}{_quoteStart}{hanzi.punctuation}{string.punctuation}\n ]")
    _ideography = re.compile(f"[{hanzi.characters}{hanzi.radicals}{zhuyin.characters}]")
    _startQuote = re.compile(f"[{_quoteStart}]")
    _number = re.compile("[0-9]")
    _alphabetical = re.compile(r"\w")

    @staticmethod
    def separateIdeograph(text):
        if text is None:
            return "", ""

        ideographic = ""
        alphabetical = ""

        last = None
        pending = ""

        for i in range(len(text)):
            char = text[i]
            if Languages._punctuation.match(char) or Languages._number.match(char):
                if Languages._startQuote.match(char) or not last:
                    pending += char
                elif last == "i":
                    ideographic += char
                else:
                    alphabetical += char
            elif Languages._ideography.match(char):
                ideographic += pending + char
                pending = ""
                last = "i"
            else:
                alphabetical += pending + char
                pending = ""
                last = "a"

        return ideographic, alphabetical

    englishStops = ".?!"
    englishEndQuotes = "[\"'”“]"
    hanziStops = hanzi.stops + englishStops
    hanziSentence = re.compile(f"[^{hanziStops}]+[{hanziStops}]")
    englishSentence = re.compile(f"([^{englishStops}]+[{englishStops}]+{englishEndQuotes}?)(\\s+|$)")
    spaces = re.compile(r"\s+")
    leadingBlanks = re.compile(r"^[\t\n ]+")
    trailingBlanks = re.compile(r"[\t\n ]+$")


    @staticmethod
    def _fixText(text):
        # Fixing spaces
        text.strip()
        text = Languages.spaces.sub(" ", text)
        text = Languages.leadingBlanks.sub("", text)
        text = Languages.trailingBlanks.sub("", text)

        # If not ended with a period, add one
        if text[-1:] not in Languages.hanziStops + Languages.englishEndQuotes:
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
            f"[^{Languages.englishStops}]([{Languages.englishStops}])((?!(\\s|[\n]|$))|(?={Languages.englishEndQuotes}))",
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
        result = Languages.hanziSentence.findall(text)
        return [Languages._recoverDots(s) for s in result]

    @staticmethod
    def englishSentences(text):
        text = Languages._fixText(text)
        text = Languages._replaceDots(text)
        # return nltk.tokenize.sent_tokenize(text)
        # My rule is better than NLTK's
        result = [s[0] for s in Languages.englishSentence.findall(text)]
        return [Languages._recoverDots(s) for s in result]

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
