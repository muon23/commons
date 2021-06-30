import unittest

import os

from work.npc.ai.utilities.Mongo import Mongo


class MongoTest(unittest.TestCase):
    mongoServer = os.environ.get("MONGO_UAT")

    def test_access(self):
        server = f"{MongoTest.mongoServer}?authSource=habitat&readPreference=primary&appname=MongoDB%20Compass&ssl=false"
        mongo = Mongo(server, "habitat")
        query = {"localId": "723eb555-b642-41a9-9ba1-69b43a041e49"}
        docs = list(mongo.get("note", query))
        print(docs)

        self.assertGreater(len(docs), 0)


if __name__ == '__main__':
    unittest.main()
