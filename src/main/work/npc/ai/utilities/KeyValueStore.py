from abc import ABC, abstractmethod
from typing import List, Dict, Union, TypeVar

import logging


class KeyValueStore(ABC):
    KeyValueStore = TypeVar("KeyValueStore")

    @staticmethod
    def of(config: str) -> KeyValueStore:
        """
        Initializes a key-value store
        :param config: URI-style configuration string
        :return: A handle to the store
        """
        from work.npc.ai.utilities.FileStore import FileStore
        from work.npc.ai.utilities.RedisStore import RedisStore

        args = config.split(":")
        storeType = args[0]

        if storeType == "redis":
            return RedisStore(args[1:])
        elif storeType == "file":
            return FileStore(args[1:])
        else:
            logging.error("unknown store type %s" % config)

    @abstractmethod
    def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    def get(self, key: str):
        pass

    @abstractmethod
    def getName(self) -> str:
        pass

    @abstractmethod
    def getKeys(self, prefix="") -> List[str]:
        pass

    @abstractmethod
    def getAll(self, prefix="") -> Dict[str, any]:
        pass

    @abstractmethod
    def put(self, key: str, value: Union[list, dict]):
        pass


