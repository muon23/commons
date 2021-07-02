import json
import os
from datetime import date
from typing import List, Union, Generator, TypeVar

from work.npc.ai.utilities import Utilities


class IncrementalStore:
    IncrementalStore = TypeVar("IncrementalStore")

    def __init__(self, name: str, storage: str):
        self.name = name
        self.storage = storage
        self.currentDate = date.today()
        self.fd = None
        self.fileName = None
        self.newDate = None

    def __del__(self):
        if self.fd is not None:
            self.fd.close()

    def getWorkingFileName(self) -> str:
        effectiveDate = self.newDate if self.newDate is not None else self.currentDate
        return os.path.join(self.storage, self.name, f"{effectiveDate}.json")

    def _getFileDescriptor(self, newDate):
        if newDate is None:
            newDate = self.newDate if self.newDate is not None else date.today()
            self.newDate = None

        if self.fd is None or self.currentDate != newDate:
            # Open new file of the day
            if self.fd is not None:
                self.fd.close()

            self.currentDate = newDate
            self.fileName = self.getWorkingFileName()
            os.makedirs(os.path.dirname(self.fileName), exist_ok=True)
            self.fd = open(self.fileName, "a")

        return self.fd

    def _write1(self, record: dict, dateField: str, dateFormat: str) -> None:
        recordTime = record.get(dateField, None) if dateField is not None else None
        recordDate = Utilities.getDate(recordTime, dateFormat)
        fd = self._getFileDescriptor(recordDate)
        record = json.dumps(record)
        fd.write(record + "\n")

    def write(
            self,
            records: Union[dict, List[dict], Generator[dict, None, None]],
            dateField: str = None,
            dateFormat: str = None
    ) -> IncrementalStore:
        if isinstance(records, dict):
            # Single record
            self._write1(records, dateField, dateFormat)
        else:
            for record in records:
                self._write1(record, dateField, dateFormat)

        return self

    def flush(self) -> IncrementalStore:
        if self.fd is not None:
            self.fd.flush()
        return self
