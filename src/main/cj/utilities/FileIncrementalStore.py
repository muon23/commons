import json
import logging
import os
import pickle
from datetime import date
from shutil import rmtree
from typing import List, Union, Generator

import yaml

from cj.utilities.IncrementalStore import IncrementalStore
from cj.utilities.TimeFormatter import TimeFormatter


class FileIncrementalStore(IncrementalStore):

    def __init__(
            self,
            path: str,
            dateField=None,
            storageFormat="pickle",
            clean: bool = False
    ):
        if storageFormat not in ["pickle", "json"]:
            raise ValueError(f"Storage format {storageFormat} not supported")

        self.path = path
        self.currentDate = date.today()
        self.dateField = dateField
        self.fd = None
        self.fileName = None
        self.newDate = None

        self.format = storageFormat

        if clean and os.path.exists(self.path):
            rmtree(self.path)

        self.access = "w" if clean else "a"
        if self.format == "pickle":
            self.access += "b"

    def __del__(self):
        if self.fd is not None:
            self.fd.close()

    def getWorkingStorageName(self) -> str:
        effectiveDate = self.newDate if self.newDate is not None else self.currentDate
        return os.path.join(self.path, f"{effectiveDate}.{self.format}")

    def _getFileDescriptor(self, newDate):
        if newDate is None:
            newDate = self.newDate if self.newDate is not None else date.today()
            self.newDate = None

        if self.fd is None or self.currentDate != newDate:
            # Open new file of the day
            if self.fd is not None:
                self.fd.close()

            self.currentDate = newDate
            self.fileName = self.getWorkingStorageName()
            os.makedirs(os.path.dirname(self.fileName), exist_ok=True)
            self.fd = open(self.fileName, self.access)

            logging.info(f"Open FileIncrementalStore {self.fileName} with access {self.access}")

        return self.fd

    def _write1(self, record: dict) -> None:
        recordTime = record.get(self.dateField, None) if self.dateField is not None else None
        recordDate = TimeFormatter.getDate(recordTime)
        fd = self._getFileDescriptor(recordDate)

        if self.format == "pickle":
            pickle.dump(record, fd)
        else:
            record = json.dumps(record, ensure_ascii=False)
            fd.write(record + "\n")

    def write(
            self,
            records: Union[dict, List[dict], Generator[dict, None, None]],
            **kwargs
    ) -> IncrementalStore:
        if isinstance(records, dict):
            # Single record
            self._write1(records)
        else:
            for record in records:
                self._write1(record)

        return self

    def flush(self) -> IncrementalStore:
        if self.fd is not None:
            self.fd.flush()
        return self

    def setLastState(self, state: dict):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        stateFile = os.path.join(self.path, "state.yml")
        with open(stateFile, "w") as fd:
            yaml.dump(state, fd)

    def getLastRecordTime(self):
        stateFile = os.path.join(self.path, "state.yml")
        if not os.path.exists(stateFile):
            return dict()
        else:
            with open(stateFile, "r") as fd:
                return yaml.load(fd)

    def read(self, startDate: str, endDate: str) -> Generator[dict, None, None]:

        for (dirPath, _, fileNames) in os.walk(self.path):
            for fn in fileNames:

                fileDate = fn.split(".")[0]
                if fileDate < startDate or fileDate > endDate:
                    continue

                filePath = os.path.join(dirPath, fn)

                if fn.endswith(".json"):
                    with open(filePath, "r") as fd:
                        for line in fd:
                            yield json.loads(line)

                elif fn.endswith(".pickle"):
                    with open(filePath, "rb") as fd:
                        while True:
                            try:
                                yield pickle.load(fd)
                            except EOFError:
                                break

    def readWithKey(self, key: str) -> dict:
        raise NotImplementedError("readWithKey() not supported by FileIncrementalStore")
