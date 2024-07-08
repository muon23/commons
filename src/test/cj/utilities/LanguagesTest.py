import unittest
from cjutil.utilities.Languages import Languages


class LanguagesTest(unittest.TestCase):
    text1 = """
    aasdf asdl asd asdfla sdfadf. asdf asdfl fasdklsdf ads... 'alskjd casd f?'\n\nyes?! 
    In Pennsylvania, Mrs. Elizabeth Burdick, a Trump supporter who owns a gun store with her husband in red-hued Mercer County, said, “Sales have been crazy.”
    The vote, 52 to 47, did not meet the 60-vote threshold. All Democrats and Kentucky Republican Sen. Rand Paul voted in opposition to the bill.
    On Friday, the E.F.L. rejected that proposal as too little, too late.
    """
    text2 = """
    He said "She said 'I am a Ph.D.!!'"
    This is useful when you want to simplify complex type signatures.
    预告：27日15时《李献计历险记》首映发布会>>>点击进入电影《李献计》首映发布会直播间(27日14时半开通)
    In contrast, NewType declares one type to be a subtype of another. 
    《#斐姨所思》每週二晚間7點30分，在《#范琪斐的美國時間》臉書粉絲團、#范琪斐 YouTube官方頻道、Clubhouse同步直播。
    資深媒體人范琪斐與夥伴們，邀大家一起上線聊聊天，關心國內外重要議題。喜歡我們的直播請別網了訂閱按讚分享、開啟小鈴鐺喔！
    Doing Derived = NewType('Derived', Original) will make the static type checker treat Derived as a subclass of Original, 
    which means a value of type Original cannot be used in places where a value of type Derived is expected. 
    This is useful when you want to prevent logic errors with minimal runtime cost.
    """

    def test_englishSentences(self):
        sentences = Languages.englishSentences(LanguagesTest.text1)
        print(sentences)
        self.assertEqual(len(sentences), 8)

    def test_sentence(self):
        testing = "\n".join([LanguagesTest.text1, LanguagesTest.text2])
        sentences = Languages.sentences(testing)

        n = 0
        for s in sentences:
            print(s)
            start, text = s
            self.assertEqual(testing[start: start+len(text)], text)
            n += 1
        self.assertEqual(n, 15)


if __name__ == '__main__':
    unittest.main()
