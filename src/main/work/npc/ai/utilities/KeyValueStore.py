from abc import ABC, abstractmethod
from typing import List, Dict


class KeyValueStore(ABC):

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


