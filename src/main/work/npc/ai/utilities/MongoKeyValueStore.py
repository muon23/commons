import pickle
from typing import Dict, Iterable

from work.npc.ai.utilities.KeyValueStore import KeyValueStore
from work.npc.ai.utilities.Mongo import Mongo


class MongoKeyValueStore(KeyValueStore):
    def __init__(
            self,
            url: str,
            collection: str,
            storageFormat="pickle",
            **kwargs
    ):
        self.url = url
        self.mongo = Mongo(url)
        self.collection = collection
        self.format = storageFormat

    def exists(self, key: any) -> bool:
        query = {"_id": key}
        return len(self.mongo.get(self.collection, query)) > 0

    def get(self, key: any):
        query = {"_id": key}
        results = self.mongo.get(self.collection, query)
        if not results:
            return None

        record = list(results)[0]
        if "pickle" in record:
            record = pickle.loads(record["pickle"])

        if "_value_" in record:
            return record["_value_"]

        record["_id"] = key
        return record

    def getName(self) -> str:
        return f"Mongo({self.url})"

    def getKeys(self) -> Iterable[str]:
        yield from self.mongo.listIds(self.collection)

    def getAll(self) -> Dict[str, any]:
        documents = self.mongo.get(self.collection, {})
        return {doc["_id"]: doc for doc in documents}

    def put(self, key: any, value: any):
        query = {"_id": key}

        if not isinstance(value, dict):
            value = {"_value_": value}

        if self.format == "pickle":
            value = {"pickle": pickle.dumps(value)}

        vv = value.copy()
        if "_id" in value:
            del vv["_id"]
        self.mongo.replace(self.collection, query, vv)

    def flush(self):
        pass

    def getNumEntries(self):
        return self.mongo.size(self.collection)
