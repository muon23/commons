import logging
import re
from typing import TypeVar, List, Union, Generator, Iterable

from bson import ObjectId
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

    def get(self, collection: str, query: dict, **kwargs):
        logging.debug(f"Querying MongoDB {self.uri}, collection {collection} with query {query}")
        return self.db[collection].find(query, **kwargs)

    def put(self, collection: str, data: Union[dict, Iterable[dict]], **kwargs) -> Iterable[ObjectId]:
        cl = self.db[collection]
        if isinstance(data, list) or isinstance(data, Generator):
            yield from cl.insert_many(data, ordered=False, **kwargs).inserted_ids
        else:
            yield cl.insert_one(data, **kwargs).inserted_id

    def index(self, collection: str, fields: List[str], unique=False):
        cl = self.db[collection]
        fields = [(f, 1) for f in fields]
        return cl.create_index(fields, unique=unique)

    def replace(self, collection: str, find: dict, data: dict):
        cl = self.db[collection]
        cl.replace_one(filter=find, replacement=data, upsert=True)

    def remove(self, collection: str, query: dict, **kwargs):
        if not query:
            return

        return self.db[collection].delete_many(query, **kwargs).deleted_count

    def clean(self, collection: str, **kwargs):
        return self.db[collection].delete_many({}, **kwargs).deleted_count

    def listIds(self, collection: str) -> Iterable[str]:
        ids = self.db[collection].distinct('_id')
        return (str(i) for i in ids)

    def size(self, collection: str) -> int:
        return self.db[collection].count_documents({})
