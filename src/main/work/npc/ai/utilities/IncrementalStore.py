import json
import os
from datetime import date
from typing import List, Union, Generator, TypeVar


class IncrementalStore:
    IncrementalStore = TypeVar("IncrementalStore")

    def __init__(self, name: str, storage: str):
        self.name = name
        self.storage = storage
        self.today = None
        self.fd = None
        self.fileName = None
        self.forcedDate = None

    def __del__(self):
        if self.fd is not None:
            self.fd.close()

    def getWorkingFileName(self) -> str:
        return os.path.join(self.storage, self.name, f"{self._getToday()}.json")

    def _getFileDescriptor(self):
        if self.fd is None or self.today != self._getToday():
            # Open new file of the day
            if self.fd is not None:
                self.fd.close()

            self.today = self._getToday()
            self.fileName = self.getWorkingFileName()
            os.makedirs(os.path.dirname(self.fileName), exist_ok=True)
            self.fd = open(self.fileName, "a")

        return self.fd

    def _write1(self, record: dict) -> None:
        fd = self._getFileDescriptor()
        record = json.dumps(record)
        fd.write(record + "\n")

    def write(self, records: Union[dict, List[dict], Generator[dict, None, None]]) -> IncrementalStore:
        if isinstance(records, dict):
            # Single record
            self._write1(records)
        else:
            for record in records:
                self._write1(record)

        return self

    def flush(self) -> IncrementalStore:
        self._getFileDescriptor().flush()
        return self

    def _setToday(self, forcedDate):
        self.forcedDate = forcedDate

    def _getToday(self):
        return self.forcedDate if self.forcedDate is not None else date.today()
