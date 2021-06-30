import os
import shutil
import unittest

from work.npc.ai.utilities.IncrementalStore import IncrementalStore


class IncrementalStoreTest(unittest.TestCase):
    outputDir = "../../../../../../output/IncrementalStoreTest"

    def setUp(self) -> None:
        # Clean up output dir if exist
        if os.path.isdir(IncrementalStoreTest.outputDir):
            shutil.rmtree(IncrementalStoreTest.outputDir)

    @staticmethod
    def lineCount(file):
        with open(file) as fd:
            return sum(1 for _ in fd)

    def test_write(self):
        data = {"a": "aaa", "b": 123, "c": 3.14159}

        inc = IncrementalStore("abc", IncrementalStoreTest.outputDir)

        # Test write a new file
        todayFile = inc.getWorkingFileName()
        if os.path.exists(todayFile):
            os.remove(todayFile)

        inc.write([data, data]).flush()
        self.assertEqual(IncrementalStoreTest.lineCount(todayFile), 2)

        # Test appending to existing file
        inc.fd.close()
        inc.fd = None
        inc.write(data).flush()

        with open(todayFile) as fd:
            lines = sum(1 for _ in fd)

        self.assertEqual(IncrementalStoreTest.lineCount(todayFile), 3)

        # Test creating new date
        newDate = "2020-01-01"
        inc._setToday(newDate)
        forcedDateFile = inc.getWorkingFileName()
        if os.path.exists(forcedDateFile):
            os.remove(forcedDateFile)

        inc.write(data).flush()

        self.assertEqual(IncrementalStoreTest.lineCount(forcedDateFile), 1)
        self.assertEqual(IncrementalStoreTest.lineCount(todayFile), 3)


if __name__ == '__main__':
    unittest.main()
