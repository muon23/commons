import os
import pickle
import shutil
import unittest
from datetime import datetime, timedelta

from work.npc.ai.utilities.IncrementalStore import IncrementalStore
from work.npc.ai.utilities.TimeFormatter import TimeFormatter


class IncrementalStoreTest(unittest.TestCase):
    outputDir = "../../../../../../output/IncrementalStoreTest"
    mongoServer = "mongodb://localhost/local"

    def setUp(self) -> None:
        # Clean up output dir if exist
        if os.path.isdir(IncrementalStoreTest.outputDir):
            shutil.rmtree(IncrementalStoreTest.outputDir)
        os.mkdir(IncrementalStoreTest.outputDir)

    @staticmethod
    def lineCount(file):
        with open(file) as fd:
            return sum(1 for _ in fd)

    def test_writeFile(self):
        data = {"a": "aaa", "b": 123, "c": 3.14159}

        inc = IncrementalStore.of(self.outputDir, collection="abc", storageFormat="json")

        # Test write a new file
        todayFile = inc.getWorkingStorageName()
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
        forcedDateFile = inc.getWorkingStorageName()
        if os.path.exists(forcedDateFile):
            os.remove(forcedDateFile)

        inc.write(data).flush()

        self.assertEqual(IncrementalStoreTest.lineCount(forcedDateFile), 1)
        self.assertEqual(IncrementalStoreTest.lineCount(todayFile), 3)

    def test_writeWithDateFieldFile(self):
        t1 = datetime.now()
        d1 = {"a": "abc", "b": 123, "date": TimeFormatter.getDate(t1)}
        t2 = t1 + timedelta(seconds=86400)
        d2 = {"a": "xyz", "b": 123, "date": TimeFormatter.getDate(t2)}

        uri = f"file:{self.outputDir}"
        inc = IncrementalStore.of(uri, collection="xyz", storageFormat="json", dateField="date")
        inc.write([d1, d1]).flush()
        d1File = inc.getWorkingStorageName()
        self.assertEqual(IncrementalStoreTest.lineCount(d1File), 2)

        inc.write([d1, d2, d2, d2]).flush()
        d2File = inc.getWorkingStorageName()
        self.assertEqual(IncrementalStoreTest.lineCount(d1File), 3)
        self.assertEqual(IncrementalStoreTest.lineCount(d2File), 3)

    def test_writePickleFile(self):
        d1 = {"a": 123, "b": "xyz"}
        d2 = {'x': 456, "y": 3.14159}

        uri = f"file:{self.outputDir}"
        inc = IncrementalStore.of(uri, collection="pqr")
        inc.write([d1, d2, d1, d2]).flush()

        outputFile = inc.getWorkingStorageName()
        with open(outputFile, "rb") as f:
            a = pickle.load(f)
            self.assertEqual(a, d1)
            a = pickle.load(f)
            self.assertEqual(a, d2)
            a = pickle.load(f)
            self.assertEqual(a, d1)
            a = pickle.load(f)
            self.assertEqual(a, d2)

    def test_mongo(self):
        t1 = datetime.now()
        d1 = {"a": "abc", "b": 123, "date": TimeFormatter.getDate(t1), "time": t1.timestamp()}
        t2 = t1 + timedelta(seconds=86400)
        d2 = {"a": "xyz", "b": 123, "date": TimeFormatter.getDate(t2), "time": t2.timestamp()}

        inc = IncrementalStore.of(
            self.mongoServer, collection="test_mongo", storageFormat="json", clean=True,
            dateField="date", uniqueFields=["a", "time"]
        )

        inc.write([d1, d1, d2])

        d2_2 = d2
        d2_2["b"] = 456
        inc.write(d2_2)

        t3 = t2 + timedelta(seconds=86400)
        d3 = {"a": "xyz", "b": 123, "date": TimeFormatter.getDate(t3), "time": t3.timestamp()}
        d3_2 = {"a": "abc", "b": 123, "date": TimeFormatter.getDate(t3), "time": t3.timestamp()}
        inc.write([d3, d2_2, d3_2])


if __name__ == '__main__':
    unittest.main()
