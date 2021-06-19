import unittest

from work.npc.ai.utilities import KeyValueStore


class KeyValueStoreTest(unittest.TestCase):

    def test_getAllFromRedis(self):
        kvs = KeyValueStore.of("redis:localhost")
        pairs = kvs.getAll("work.npc.ai.metrics.UserProfile")
        self.assertGreater(len(pairs), 50)

        for p in pairs:
            print(p, pairs[p].id.id, pairs[p].name)

    def test_readWriteRedis(self):
        kvs = KeyValueStore.of("redis:localhost")
        testing = {
            "a": 10,
            "b": "xyz"
        }
        kvs.put("test_readWriteRedis", testing)

        readBack = kvs.get("test_readWriteRedis", valueFormat="json")
        print(readBack)
        self.assertEqual(readBack, testing)


if __name__ == '__main__':
    unittest.main()
