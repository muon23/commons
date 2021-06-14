import os
import unittest

from work.npc.ai.utilities import Utilities


class UtilitiesTest(unittest.TestCase):
    def test_withEnvironment(self):
        argument = {
            "x": "abcd/${AAA_123:aaa_123}/de/${XXX_456}/${ZZZ:zzz}/${WWW}",
            "y": {
                "y1": "${BBB:222}",
                "y2": "abcde",
                "y3": "${XXX_456:ccc}",
            }
        }

        os.environ.setdefault("AAA_123", "bbb")
        os.environ.setdefault("XXX_456", "999")

        Utilities.withEnvironment(argument)

        print(argument)

        self.assertEqual(
            argument,
            {'x': 'abcd/bbb/de/999/zzz/${WWW}', 'y': {'y1': '222', 'y2': 'abcde', 'y3': '999'}}
        )

    def test_md5Of(self):
        md5 = Utilities.md5Of(".", verbose=True)
        print(md5)
        self.assertEqual(len(md5), 32)


if __name__ == '__main__':
    unittest.main()
