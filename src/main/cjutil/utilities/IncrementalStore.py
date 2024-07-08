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
        from cjutil.utilities.FileIncrementalStore import FileIncrementalStore
        from cjutil.utilities.MongoIncrementalStore import MongoIncrementalStore

        url = urlparse(uri)

        if not url.scheme or url.scheme == "file":
            if uniqueFields:
                logging.warning(f"uniqueFields {uniqueFields} not supported using FileIncrementalStore")

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
            records: Union[dict, List[dict], Generator[dict, None, None]],
            **kwargs
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

    @abstractmethod
    def read(self, startDate: str, endDate: str) -> Generator[dict, None, None]:
        pass

    @abstractmethod
    def readWithKey(self, key: str) -> dict:
        pass
