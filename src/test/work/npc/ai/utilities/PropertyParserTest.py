import os
import unittest

from work.npc.ai.utilities.PropertyParser import PropertyParser


class MyTestCase(unittest.TestCase):
    def test_basic(self):
        os.environ.setdefault("MONGO_URL", "<something here>")
        result = PropertyParser.parse("::ccc:${AAA:xyz: cccc ${MONGO_URL:}}aaaa:bbb")
        print(result)
        self.assertEqual(result, "::ccc:xyz: cccc <something here>aaaa:bbb")

        result = PropertyParser.parse("${MONGO_URL:}${MONGO_URL}")
        print(result)
        self.assertEqual(result, "<something here><something here>")

        result = PropertyParser.parse("aaa")
        print(result)
        self.assertEqual(result, "aaa")

        result = PropertyParser.parse(":::::")
        print(result)
        self.assertEqual(result, ":::::")

        with self.assertRaises(RuntimeError):
            PropertyParser.parse("}}")


if __name__ == '__main__':
    unittest.main()
