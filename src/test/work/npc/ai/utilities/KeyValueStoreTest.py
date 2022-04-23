import unittest
from typing import List

from work.npc.ai.utilities.KeyValueStore import KeyValueStore


class KeyValueStoreTest(unittest.TestCase):

    outputDir = "../../../../../../output/KeyValueStoreTest"
    mongoServer = "mongodb://localhost/local"

    data: List[dict] = [
        {"_id": 1, "a": 123},
        {"_id": 2, "a": 456},
        {"_id": 3, "a": 789},
        {"_id": 9, "a": 987},
    ]

    def test_getAllFromRedis(self):
        kvs = KeyValueStore.of("redis://localhost", collection="work.npc.ai.metrics.UserProfile")
        pairs = kvs.getAll()
        self.assertGreater(len(pairs), 50)

        for key in pairs:
            profile = kvs.get(key)
            print(key, str(profile.period))

    def __doTest(self, url, **kwargs):
        kvs = KeyValueStore.of(url, **kwargs)

        for d in self.data:
            kvs.put(d["_id"], d)

        readBack = kvs.get(2)
        print(readBack)
        self.assertEqual(readBack, self.data[1])

        pairs = kvs.getAll()
        self.assertEqual(len(pairs), len(self.data))

    def test_readWriteRedisPickle(self):
        self.__doTest("redis://localhost", collection="test_readWriteRedisPickle")

    def test_readWriteRedisJson(self):
        self.__doTest("redis://localhost", collection="test_readWriteRedisJson", storageFormat="json")

    def __doFileTest(self, url, **kwargs):
        kvsw = KeyValueStore.of(url, access="w", **kwargs)

        for d in self.data:
            kvsw.put(d["_id"], d)
        kvsw.flush()

        kvsr = KeyValueStore.of(url, access="r", **kwargs)
        readBack = kvsr.get(2)
        print(readBack)
        self.assertEqual(readBack, self.data[1])

        pairs = kvsr.getAll()
        self.assertEqual(len(pairs), len(self.data))

    def test_readWriteFileJson(self):
        self.__doFileTest(f"{self.outputDir}", collection="test_readWriteFileJson.json")

    def test_readWriteFilePickle(self):
        self.__doFileTest(f"file:{self.outputDir}", collection="test_readWriteFilePickle.pickle")

    def test_mongoJson(self):
        self.__doTest(self.mongoServer, collection="test_mongoKVJson", storageFormat="json")

    def test_mongoPickle(self):
        self.__doTest(self.mongoServer, collection="test_mongoKVPickle")

    def test_mongoFragment(self):
        something = "".join("0123456789" * 5000000)
        value = {
            "_id": "abcde",
            "something": something
        }
        mongo = KeyValueStore.of("mongodb://localhost/local", collection="testMongoFragment", storageFormat="pickle")
        mongo.put(value["_id"], value)

        readBack = mongo.get(value["_id"])

        self.assertEqual(readBack, value)


if __name__ == '__main__':
    unittest.main()
