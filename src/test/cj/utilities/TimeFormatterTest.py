import unittest

from cjutil.utilities.TimeFormatter import TimeFormatter


class TimeFormatterTest(unittest.TestCase):
    def test_duration(self):
        self.assertEqual(TimeFormatter.getDuration("5"), 5)
        self.assertEqual(TimeFormatter.getDuration("1.5s"), 1.5)
        self.assertEqual(TimeFormatter.getDuration("3m"), 180)
        self.assertEqual(TimeFormatter.getDuration("2h"), 7200)
        self.assertEqual(TimeFormatter.getDuration("1d"), 86400)
        self.assertEqual(TimeFormatter.getDuration("2w"), 14 * 86400)
        self.assertEqual(TimeFormatter.getDuration("2M"), 60 * 86400)

    def test_dateAfterDays(self):
        self.assertEqual(TimeFormatter.getDateAfterDays("2021-12-30", 3), "2022-01-02")
        self.assertEqual(TimeFormatter.getDateAfterDays("2021-12-01", -3), "2021-11-28")


if __name__ == '__main__':
    unittest.main()
