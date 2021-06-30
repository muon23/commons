import unittest

from work.npc.ai.utilities.KeyValueStore import KeyValueStore


class KeyValueStoreTest(unittest.TestCase):

    def test_getAllFromRedis(self):
        kvs = KeyValueStore.of("redis:localhost")
        pairs = kvs.getAll("work.npc.ai.metrics.UserProfile")
        self.assertGreater(len(pairs), 50)

        for p in pairs:
            print(p, pairs[p].name.name, pairs[p].name)

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

    def test_readJavaObjFile(self):
        kvs = KeyValueStore.of("file:../../../../../../output/testSaveAndLoad")

        everything = kvs.getAll()

        print(everything)
        self.assertGreater(len(everything), 0)
        self.assertEqual(everything["one"], 1)
        self.assertEqual(everything["pi"].value, 3.14159)

        # self.assertGreater(len(keys), 1000)
        # self.assertTrue(kvs.exists("work.npc.ai.measures.ChatCounts.11.23.2020-07-04"))
        # self.assertIsNotNone(kvs.get("work.npc.ai.measures.ChatCounts.19.36.2020-06-18"))

        # cc = ChatCounts(kvs, 19, 36, "2020-06-18")
        # print(cc.getChatCount(), cc.getWordCount())
        # self.assertTrue(cc.getChatCount() >= 10 and cc.getWordCount() >= 8)
        #
        # ua = UserActivities(kvs, 29)
        # receivers = ua.getReceivers()
        # self.assertGreaterEqual(len(receivers), 10)
        # print([ua.getReceiverName(r) for r in receivers])
        #
        # print([ua.getSentChatCount(r) for r in receivers if not ua.getReceiverName(r).startswith("@npc")])

if __name__ == '__main__':
    unittest.main()
