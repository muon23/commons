from typing import TypeVar

import pymongo


class Mongo:
    Mongo = TypeVar("Mongo")

    def __init__(self, uri: str, database: str):
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[database]

    def get(self, collection: str, query: dict):
        return self.db[collection].find(query)
