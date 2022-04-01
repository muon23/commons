import logging
import pickle
from typing import Union, List, Generator

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
            self.forIndexing = {dateField}
            self.mongo.index(self.collection, [dateField])

        if uniqueFields:
            self.forIndexing = self.forIndexing.union(set(uniqueFields))
            self.mongo.index(self.collection, uniqueFields, unique=True)

    def __prepare(
            self,
            records: Union[dict, List[dict], Generator[dict, None, None]],
    ) -> Generator[dict, None, None]:
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
            records: Union[dict, List[dict], Generator[dict, None, None]],
    ) -> IncrementalStore:
        try:
            self.mongo.put(self.collection, self.__prepare(records))
        except Exception as e:
            logging.debug(e)
            pass
        return self

    def flush(self) -> IncrementalStore:
        return self

    def getWorkingStorageName(self) -> str:
        return self.collection

    def setLastState(self, state: dict):
        state["collection"] = self.collection
        self.mongo.index(self.STATE_COLLECTION, ["collection"], unique=True)
        self.mongo.replace(self.STATE_COLLECTION, {"collection": self.collection}, state)

    def getLastRecordTime(self):
        query = {"collection": self.collection}
        state = self.mongo.get(self.STATE_COLLECTION, query)
        return state[0] if state else dict()
