import unittest

import os

from work.npc.ai.utilities.KeyValueStore import KeyValueStore


class KeyValueStoreTest(unittest.TestCase):

    outputDir = "../../../../../../output/KeyValueStoreTest"

    def test_getAllFromRedis(self):
        kvs = KeyValueStore.of("redis:localhost")
        pairs = kvs.getAll("work.npc.ai.metrics.UserProfile")
        self.assertGreater(len(pairs), 50)

        for key in pairs:
            profile = kvs.get(key)
            print(key, str(profile.name))

    def test_readWriteRedis(self):
        kvs = KeyValueStore.of("redis:localhost:::json")
        testing = {
            "a": 10,
            "b": "xyz"
        }
        kvs.put("test_readWriteRedis", testing)

        readBack = kvs.get("test_readWriteRedis")
        print(readBack)
        self.assertEqual(readBack, testing)

    def test_readWriteRedisPickle(self):
        kvs = KeyValueStore.of("redis:localhost:::pickle")
        testing = {
            "a": 10,
            "b": "xyz"
        }
        kvs.put("test_readWriteRedisPickle", testing)

        readBack = kvs.get("test_readWriteRedisPickle")
        print(readBack)
        self.assertEqual(readBack, testing)

    def test_readWriteFileJson(self):
        outputFile = self.outputDir + "/test_readWriteFileJson.json"
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)

        kvs = KeyValueStore.of(f"file:{outputFile}:w:json")
        testing = {
            "a": 10,
            "b": "xyz"
        }
        kvs.put("test_readWriteRedisPickle", testing)
        del kvs

        kvs2 = KeyValueStore.of(f"file:{outputFile}:r:json")
        readBack = kvs2.get("test_readWriteRedisPickle")
        print(readBack)
        self.assertEqual(readBack, testing)

    def test_readWriteFilePickle(self):
        outputFile = self.outputDir + "/test_readWriteFilePickle.pickle"
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)

        kvs = KeyValueStore.of(f"file:{outputFile}:w:pickle")
        testing = {
            "a": 10,
            "b": "xyz"
        }
        kvs.put("test_readWriteRedisPickle", testing)
        del kvs

        kvs2 = KeyValueStore.of(f"file:{outputFile}:r:pickle")
        readBack = kvs2.get("test_readWriteRedisPickle")
        print(readBack)
        self.assertEqual(readBack, testing)

    def test_readJavaObjFile(self):
        kvs = KeyValueStore.of("file:../../../../../../output/testSaveAndLoad")

        everything = kvs.getAll()

        print(everything)
        self.assertGreater(len(everything), 0)
        self.assertEqual(everything["one"], 1)
        self.assertEqual(everything["pi"].value, 3.14159)


if __name__ == '__main__':
    unittest.main()
