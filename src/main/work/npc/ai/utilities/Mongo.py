import logging
import re
from typing import TypeVar

import pymongo


class Mongo:
    Mongo = TypeVar("Mongo")

    def __init__(self, uri: str, database: str = None):
        if database is None:
            m = re.search(r"mongodb://[^/]+/(\w+)($|\?)", uri)
            if len(m.groups()) < 1:
                raise ValueError(f"Missing database info in {uri}")
            database = m[1] if len(m.groups()) >= 1 else None

        self.uri = uri
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[database]

    def get(self, collection: str, query: dict):
        logging.info(f"Querying MongoDB {self.uri}, collection {collection} with query {query}")
        return self.db[collection].find(query)
