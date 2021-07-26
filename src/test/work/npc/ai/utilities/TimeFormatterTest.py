import unittest

from work.npc.ai.utilities.TimeFormatter import TimeFormatter


class TimeFormatterTest(unittest.TestCase):
    def test_duration(self):
        self.assertEqual(TimeFormatter.getDuration("5"), 5)
        self.assertEqual(TimeFormatter.getDuration("1.5s"), 1.5)
        self.assertEqual(TimeFormatter.getDuration("3m"), 180)
        self.assertEqual(TimeFormatter.getDuration("2h"), 7200)
        self.assertEqual(TimeFormatter.getDuration("1d"), 86400)
        self.assertEqual(TimeFormatter.getDuration("2w"), 14 * 86400)
        self.assertEqual(TimeFormatter.getDuration("2M"), 60 * 86400)

if __name__ == '__main__':
    unittest.main()
