import os
import unittest
from datetime import datetime

from cjutil.utilities import Utilities
from cjutil.utilities.TimeFormatter import TimeFormatter


class UtilitiesTest(unittest.TestCase):
    def test_withEnvironment(self):
        argument = {
            "x": "abcd/${AAA_123:aaa_123}/de/${XXX_456}/${ZZZ:zzz}/${WWW}",
            "y": {
                "y1": "${BBB:file:${AAA_123}}/456",
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
            {'x': 'abcd/bbb/de/999/zzz/', 'y': {'y1': 'file:bbb/456', 'y2': 'abcde', 'y3': '999'}}
        )

    def test_md5Of(self):
        md5 = Utilities.md5Of(".", verbose=True)
        print(md5)
        self.assertEqual(len(md5), 32)

    def test_getDate(self):
        d = TimeFormatter.getDate("12/25/20", "%m/%d/%y")
        self.assertEqual(d, "2020-12-25")
        d = TimeFormatter.getDate(1625197438)
        self.assertEqual(d, "2021-07-01")
        d = TimeFormatter.getDate(1625197438123)
        self.assertEqual(d, "2021-07-01")
        d = TimeFormatter.getDate("2021-07-01T20:55:02", ["%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S"])
        self.assertEqual(d, "2021-07-01")
        dt = datetime(2021, 7, 1, 20, 50, 10).isoformat()
        d = TimeFormatter.getDate(dt)
        self.assertEqual(d, "2021-07-01")
        d = TimeFormatter.getDate("2020-05-14T00:39:18.349+00:00")
        self.assertEqual(d, "2020-05-14")

if __name__ == '__main__':
    unittest.main()
