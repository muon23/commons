import os
import pickle
import shutil
import unittest
from datetime import datetime, timedelta

from work.npc.ai.utilities.IncrementalStore import IncrementalStore


class IncrementalStoreTest(unittest.TestCase):
    outputDir = "../../../../../../output/IncrementalStoreTest"

    def setUp(self) -> None:
        # Clean up output dir if exist
        if os.path.isdir(IncrementalStoreTest.outputDir):
            shutil.rmtree(IncrementalStoreTest.outputDir)
        os.mkdir(IncrementalStoreTest.outputDir)

    @staticmethod
    def lineCount(file):
        with open(file) as fd:
            return sum(1 for _ in fd)

    def test_write(self):
        data = {"a": "aaa", "b": 123, "c": 3.14159}

        inc = IncrementalStore("abc", IncrementalStoreTest.outputDir, "json")

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
        inc.newDate = newDate
        forcedDateFile = inc.getWorkingFileName()
        if os.path.exists(forcedDateFile):
            os.remove(forcedDateFile)

        inc.write(data).flush()

        self.assertEqual(IncrementalStoreTest.lineCount(forcedDateFile), 1)
        self.assertEqual(IncrementalStoreTest.lineCount(todayFile), 3)

    def test_writeWithDateField(self):
        t1 = datetime.now()
        d1 = {"a": "abc", "b": 123, "date": t1.isoformat()}
        t2 = t1 + timedelta(seconds=86400)
        d2 = {"a": "xyz", "b": 123, "date": t2.isoformat()}

        inc = IncrementalStore("xyz", IncrementalStoreTest.outputDir, "json")
        inc.write([d1, d1], dateField="date").flush()
        d1File = inc.getWorkingFileName()
        self.assertEqual(IncrementalStoreTest.lineCount(d1File), 2)

        inc.write([d1, d2, d2, d2], dateField="date").flush()
        d2File = inc.getWorkingFileName()
        self.assertEqual(IncrementalStoreTest.lineCount(d1File), 3)
        self.assertEqual(IncrementalStoreTest.lineCount(d2File), 3)

    def test_writePickle(self):
        d1 = {"a": 123, "b": "xyz"}
        d2 = {'x': 456, "y": 3.14159}

        inc = IncrementalStore("pqr", IncrementalStoreTest.outputDir)
        inc.write([d1, d2, d1, d2]).flush()

        outputFile = inc.getWorkingFileName()
        with open(outputFile, "rb") as f:
            a = pickle.load(f)
            self.assertEqual(a, d1)
            a = pickle.load(f)
            self.assertEqual(a, d2)
            a = pickle.load(f)
            self.assertEqual(a, d1)
            a = pickle.load(f)
            self.assertEqual(a, d2)



if __name__ == '__main__':
    unittest.main()
