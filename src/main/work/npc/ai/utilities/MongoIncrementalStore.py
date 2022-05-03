import logging
import pickle
from typing import Union, Generator, Iterable

from work.npc.ai.utilities.IncrementalStore import IncrementalStore
from work.npc.ai.utilities.Mongo import Mongo


class MongoIncrementalStore(IncrementalStore):
    STATE_COLLECTION = "state"

    def __init__(
            self,
            mongoUrl: str,
            collection: str,
            storageFormat="pickle",
            clean=False,
            dateField="date",
            uniqueFields=None,
    ):
        self.url = mongoUrl
        self.mongo = Mongo(mongoUrl)
        self.collection = collection
        self.storageFormat = storageFormat

        if clean:
            self.mongo.clean(self.collection)

        if dateField:
            self.dateField = dateField
            self.forIndexing = {dateField}
            self.mongo.index(self.collection, [dateField])

        if uniqueFields:
            self.uniqueFields = uniqueFields
            self.forIndexing = self.forIndexing.union(set(uniqueFields))
            self.mongo.index(self.collection, uniqueFields, unique=True)

    def __prepare(self, records: Union[dict, Iterable[dict]]) -> Iterable[dict]:
        if isinstance(records, dict):
            records = [records]

        for rec in records:
            if self.storageFormat not in ["pickle"]:
                yield rec
            else:
                idxFields = {col: rec[col] for col in self.forIndexing}
                yield {
                    "pickle": pickle.dumps(rec),
                    **idxFields
                }

    def write(
            self,
            records: Union[dict, Iterable[dict]],
            **kwargs
    ) -> IncrementalStore:

        try:
            if self.uniqueFields and kwargs.get("replace"):
                for rec in self.__prepare(records):
                    query = {uf: rec[uf] for uf in self.uniqueFields }
                    self.mongo.replace(self.collection, query, rec)
            else:
                list(self.mongo.put(self.collection, self.__prepare(records)))  # list() to trigger put to do something

        except Exception as e:
            logging.debug(e)
            pass
        return self

    def flush(self) -> IncrementalStore:
        return self

    def getWorkingStorageName(self) -> str:
        return self.collection

    def setLastState(self, state: dict):
        state["_id"] = self.collection
        self.mongo.replace(self.STATE_COLLECTION, {"_id": self.collection}, state)

    def getLastRecordTime(self):
        query = {"_id": self.collection}
        state = self.mongo.get(self.STATE_COLLECTION, query)
        return state[0] if state else dict()

    def read(self, startDate: str = None, endDate: str = None) -> Generator[dict, None, None]:

        query = {}
        if self.dateField:
            dateRange = dict()
            if startDate:
                dateRange.update({"$gte": startDate})
            if endDate:
                dateRange.update({"$lte": endDate})

            if dateRange:
                query.update({self.dateField: dateRange})

        for record in self.mongo.get(self.collection, query=query):
            if "pickle" in record:
                r = {"_id": record["_id"]}
                r.update(pickle.loads(record["pickle"]))
                yield r
            else:
                yield record

    def readWithKey(self, key: str) -> dict:
        query = {"_id": key}
        results = self.mongo.get(self.collection, query=query)
        return results[0] if results else dict()
