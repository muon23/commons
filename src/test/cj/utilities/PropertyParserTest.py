import os
import unittest

from cjutil.utilities.PropertyParser import PropertyParser


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

        result = PropertyParser.parse("${not here}")
        print(result)
        self.assertEqual(result, None)

        with self.assertRaises(RuntimeError):
            PropertyParser.parse("}}")


if __name__ == '__main__':
    unittest.main()
