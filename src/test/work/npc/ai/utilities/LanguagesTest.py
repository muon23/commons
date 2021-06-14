import unittest
from work.npc.ai.utilities.Languages import Languages

class LanguagesTest(unittest.TestCase):
    def test_englishSentences(self):
        text = """
        aasdf asdl asd asdfla sdfadf. asdf asdfl fasdklsdf ads... 'alskjd casd f?'\n\nyes?! 
        In Pennsylvania, Mrs. Elizabeth Burdick, a Trump supporter who owns a gun store with her husband in red-hued Mercer County, said, “Sales have been crazy.”
        The vote, 52 to 47, did not meet the 60-vote threshold. All Democrats and Kentucky Republican Sen. Rand Paul voted in opposition to the bill.
        On Friday, the E.F.L. rejected that proposal as too little, too late.
        """
        sentences = Languages.englishSentences(text)
        print(sentences)
        self.assertEqual(len(sentences), 8)


    def test_w(self):
        def w(power, base, terms):
            for i in range(1, terms+1):
                digits = 0
                dividends = set()
                dividend = 1
                divisor = i ** power
                remainder = dividend % divisor

                while dividend not in dividends and remainder != 0:
                    digits += 1
                    dividends.add(dividend)
                    dividend *= base
                    remainder = dividend % divisor
                    dividend = remainder

                yield digits

        print(list(w(3, 10, 100)))


if __name__ == '__main__':
    unittest.main()
