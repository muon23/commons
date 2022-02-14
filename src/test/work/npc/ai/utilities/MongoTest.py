import unittest

import os

from work.npc.ai.utilities.Mongo import Mongo


class MongoTest(unittest.TestCase):
    mongoUat = os.environ.get("MONGO_UAT")
    mongoProd = os.environ.get("MONGO_PROD")

    def test_aws_access(self):
        mongoAws = "mongodb://tanka:CtgC8X5QxD8R5fvx@dev-tanka-sg-docdb.aws.tankaapps.com:27017/habitat"
        server = f"{mongoAws}?authSource=habitat&readPreference=primary&appname=MongoDB%20Compass&ssl=false"
        mongo = Mongo(server, "habitat")
        query = {"localId": "723eb555-b642-41a9-9ba1-69b43a041e49"}
        docs = list(mongo.get("note", query))
        print(docs)

        self.assertGreater(len(docs), 0)

    def test_access(self):
        server = f"{self.mongoUat}?authSource=habitat&readPreference=primary&appname=MongoDB%20Compass&ssl=false"
        mongo = Mongo(server, "habitat")
        query = {"localId": "723eb555-b642-41a9-9ba1-69b43a041e49"}
        docs = list(mongo.get("note", query))
        print(docs)

        self.assertGreater(len(docs), 0)

    def test_accessImageCaptions(self):
        server = f"{self.mongoProd}?authSource=habitat&readPreference=primary&appname=MongoDB%20Compass&ssl=false"
        mongo = Mongo(server, "habitat")
        query = {}
        docs = list(mongo.get("ImageVideoSearch", query))
        for doc in docs:
            print("====")
            print(f"{doc['OCR']} -- {doc['ImageCaption']}")


if __name__ == '__main__':
    unittest.main()
