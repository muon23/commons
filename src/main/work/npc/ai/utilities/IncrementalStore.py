import logging
import os
from abc import ABC, abstractmethod
from typing import Union, List, Generator, TypeVar
from urllib.parse import urlparse


class IncrementalStore(ABC):
    IncrementalStore = TypeVar("IncrementalStore")

    @classmethod
    def of(
            cls,
            uri: str,
            collection: str,
            storageFormat: str = "pickle",
            clean: bool = False,
            dateField: str = None,
            uniqueFields: List[str] = None,
    ):
        from work.npc.ai.utilities.FileIncrementalStore import FileIncrementalStore
        from work.npc.ai.utilities.MongoIncrementalStore import MongoIncrementalStore

        url = urlparse(uri)

        if not url.scheme or url.scheme == "file":
            return FileIncrementalStore(
                os.path.join(url.path, collection),
                storageFormat=storageFormat,
                clean=clean,
                dateField=dateField,
            )

        elif url.scheme == "mongodb":
            return MongoIncrementalStore(
                uri,
                collection=collection,
                storageFormat=storageFormat,
                clean=clean,
                dateField=dateField,
                uniqueFields=uniqueFields,
            )

        else:
            logging.error("Unknown store type %s" % url.scheme)

    @abstractmethod
    def write(
        self,
        records: Union[dict, List[dict], Generator[dict, None, None]]
    ) -> IncrementalStore:
        pass

    @abstractmethod
    def flush(self) -> IncrementalStore:
        pass

    @abstractmethod
    def getWorkingStorageName(self) -> str:
        pass

    @abstractmethod
    def setLastState(self, state: dict):
        pass

    @abstractmethod
    def getLastRecordTime(self):
        pass
