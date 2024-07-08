import logging
from abc import ABC, abstractmethod
from typing import Dict, TypeVar, Iterable
from urllib.parse import urlparse


class KeyValueStore(ABC):
    KeyValueStore = TypeVar("KeyValueStore")

    @staticmethod
    def of(
            uri: str,
            collection: str,
            **kwargs
    ) -> KeyValueStore:
        from cjutil.utilities.FileKeyValueStore import FileKeyValueStore
        from cjutil.utilities.RedisStore import RedisStore
        from cjutil.utilities.MongoKeyValueStore import MongoKeyValueStore

        url = urlparse(uri)

        if not url.scheme or url.scheme == "file":
            return FileKeyValueStore(path=url.path, file=collection, **kwargs)
        elif url.scheme == "redis":
            return RedisStore(uri, collection=collection, **kwargs)
        elif url.scheme == "mongodb":
            return MongoKeyValueStore(uri, collection=collection, **kwargs)
        else:
            logging.error("Unknown store type %s" % url.scheme)

    @abstractmethod
    def exists(self, key: any) -> bool:
        pass

    @abstractmethod
    def get(self, key: any):
        pass

    @abstractmethod
    def getName(self) -> str:
        pass

    @abstractmethod
    def getKeys(self) -> Iterable[any]:
        pass

    @abstractmethod
    def getAll(self) -> Dict[any, any]:
        pass

    @abstractmethod
    def put(self, key: any, value: any):
        pass

    @abstractmethod
    def flush(self):
        pass

    @abstractmethod
    def getNumEntries(self):
        pass


