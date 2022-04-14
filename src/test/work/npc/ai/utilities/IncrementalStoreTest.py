import os
import pickle
import shutil
import unittest
from datetime import timedelta

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

    def __makeDatedData(self, startDate, numDays, recordsPerDay, names):
        startTime = TimeFormatter.getDateTime(startDate)
        timeInterval = 24 / recordsPerDay
        recordSpace = timeInterval / len(names)

        data = []
        for day in range(numDays):
            for i in range(recordsPerDay):
                t = startTime + timedelta(hours=24 * day + timeInterval * i)
                for n in names:
                    data += [
                        {"period": n, "b": 123, "date": TimeFormatter.getDate(t), "time": TimeFormatter.getTimestamp(t)},
                    ]
                    t = t + timedelta(hours=recordSpace)
        return data

    def test_readWriteDatedRecords(self):
        recordsPerDay = 20
        names = ["aaa", "bbb"]
        recordsPerFile = recordsPerDay * len(names)

        data = self.__makeDatedData("2022-01-01", 10, recordsPerDay, names)

        uri = f"file:{self.outputDir}"
        inc = IncrementalStore.of(
            uri, collection="test_readwriteDatedRecord",
            storageFormat="json", dateField="date", uniqueFields=["period", "time"]
        )

        # Test writing.  d1File is the last file written, and should have 40 entries
        inc.write(data).flush()
        d1File = inc.getWorkingStorageName()
        self.assertEqual(IncrementalStoreTest.lineCount(d1File), recordsPerFile)

        # Write again and we should have double the data, since FileIncrementalStore does not check for uniquness
        inc.write(data).flush()
        d2File = inc.getWorkingStorageName()
        self.assertEqual(IncrementalStoreTest.lineCount(d2File), 2 * recordsPerFile)

        # Open another incremental store that cleans existing data
        inc = IncrementalStore.of(
            uri, collection="test_readwriteDatedRecord",
            storageFormat="json", dateField="date", clean=True
        )

        # Test writing again and should have 40 entries because the old ones are removed
        inc.write(data).flush()
        d1File = inc.getWorkingStorageName()
        self.assertEqual(IncrementalStoreTest.lineCount(d1File), 40)

        # Read the data back.  Reopen without storage format and it should figure this out by itself.
        inc = IncrementalStore.of(
            uri, collection="test_readwriteDatedRecord", dateField="date"
        )

        readData = list(inc.read("2022-01-02", "2022-01-03"))
        self.assertEqual(len(readData), 2 * recordsPerFile)  # Having 2 days of data
        for r in readData:
            self.assertIn(r["date"], ["2022-01-02", "2022-01-03"])

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
        recordsPerDay = 5
        names = ["aaa", "bbb"]
        recordsPerFile = recordsPerDay * len(names)

        data = self.__makeDatedData("2022-01-01", 5, recordsPerDay, names)

        inc = IncrementalStore.of(
            self.mongoServer, collection="test_mongo",
            storageFormat="json", dateField="date", uniqueFields=["period", "time"], clean=True
        )

        # Test writing.  d1File is the last file written, and should have 40 entries
        inc.write(data).flush()

        # Open another incremental store in pickle format.  Write some data that are not unique
        data2 = self.__makeDatedData("2022-01-04", 5, recordsPerDay, names)
        inc2 = IncrementalStore.of(
            self.mongoServer, collection="test_mongo",
            storageFormat="pickle", dateField="date", uniqueFields=["period", "time"],
        )
        inc2.write(data2, replace=True).flush()

        # Read the data back.  Reopen without storage format and it should figure this out by itself.
        inc3 = IncrementalStore.of(
            self.mongoServer, collection="test_mongo", dateField="date"
        )

        readData = list(inc3.read("2022-01-03", "2022-01-04"))
        self.assertEqual(len(readData), 2 * recordsPerFile)  # Having 2 days of data
        for r in readData:
            self.assertIn(r["date"], ["2022-01-03", "2022-01-04"])  # 2022-01-04 shall be decoded from pickle format
            self.assertEqual(len(r), 5)  # 4 fields plus "_id"


if __name__ == '__main__':
    unittest.main()
