import logging
import pickle
import sys
from operator import itemgetter
from typing import Dict, Iterable, List

from pymongo.errors import DocumentTooLarge

from work.npc.ai.utilities.KeyValueStore import KeyValueStore
from work.npc.ai.utilities.Mongo import Mongo


class MongoKeyValueStore(KeyValueStore):
    MAX_DOCUMENT_SIZE = 16000000 - 1000  # 16M-byte BSON limit with 1K overhead

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

        self.mongo.index(self.collection, ["_key_"])

    def exists(self, key: any) -> bool:
        query = {"_key_": key}
        return len(self.mongo.get(self.collection, query)) > 0

    def get(self, key: any):
        query = {"_key_": key}
        results = self.mongo.get(self.collection, query)
        record = self.__reassemble(list(results))

        if not record:
            return None

        if "_value_" in record:
            return record["_value_"]

        record["_id"] = record.pop("_id_") if "_id_" in record else key
        if "_key_" in record:
            record.pop("_key_")

        return record

    def getName(self) -> str:
        return f"Mongo({self.url})"

    def getKeys(self) -> Iterable[str]:
        yield from self.mongo.listIds(self.collection)

    def getAll(self) -> Dict[str, any]:
        documents = self.mongo.get(self.collection, {})
        return {doc["_id"]: doc for doc in documents}

    def put(self, key: any, value: any):
        if not isinstance(value, dict):
            value = {"_value_": value}

        for record in self.__fragment(value):

            query = {"_id": "_".join(filter(None, [str(key), str(record.get('_fragment_', None))]))}
            record["_key_"] = key

            if "_id" in record:
                record["_id_"] = record.pop("_id")

            try:
                self.mongo.replace(self.collection, query, record)
            except DocumentTooLarge as e:
                size = sys.getsizeof(record)
                logging.error(f"Trying to save {size} bytes of key {key} to collection {self.collection}")
                raise RuntimeError(str(e))

    def __fragment(self, value: dict) -> Iterable[dict]:
        if self.format == "json":
            if sys.getsizeof(value) <= self.MAX_DOCUMENT_SIZE:
                yield value.copy()
                return

        if self.format == "pickle":
            payload = pickle.dumps(value)
        else:
            raise NotImplementedError(f"Unsupported format {self.format}")

        k = 0
        i = 0
        while k < len(payload):
            yield {
                "_fragment_": i,
                self.format: payload[k: k + self.MAX_DOCUMENT_SIZE]
            }
            k += self.MAX_DOCUMENT_SIZE
            i += 1

    @classmethod
    def __reassemble(cls, fragments: List[dict]) -> dict:
        if not fragments:
            return dict()

        if "pickle" in fragments[0]:
            storageFormat = "pickle"
        else:  # JSON, can't be reassembled
            return fragments[0]

        if not all([storageFormat in f for f in fragments]):
            logging.warning(f"Not all fragments has a {storageFormat} field, ignored")
            return dict()

        if not all(["_fragment_" in f for f in fragments]):
            logging.warning(f"Not all fragments has a _key_ and _fragment_ fields, ignored")
            return dict()

        fragments = sorted(fragments, key=itemgetter("_fragment_"))
        payload = bytearray(0)
        for f in fragments:
            payload.extend(f.get(storageFormat))

        if storageFormat == "pickle":
            return pickle.loads(payload)
        else:
            # Will never be here
            assert False

    def flush(self):
        pass

    def getNumEntries(self):
        return self.mongo.size(self.collection)
