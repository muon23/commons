from typing import Union

import javaobj.v2 as javaobj
import json

from work.npc.ai.utilities.KeyValueStore import KeyValueStore


class FileStore(KeyValueStore):

    def __init__(self, args):

        if len(args) != 1:
            raise RuntimeError("Key-value store file name required")

        self.path = args[0]
        with open(self.path, "rb") as fd:
            self.map = javaobj.load(fd)

    def exists(self, key):
        return key in self.map

    def get(self, key, valueFormat: str = "javaobj"):
        data = bytes([x % 256 for x in self.map[key]])
        if valueFormat == "javaobj":
            return javaobj.loads(data)
        elif valueFormat == "json":
            return json.loads(data)

    def getName(self):
        return f"File({self.path})"

    def getKeys(self, prefix=""):
        keys = [str(key) for key in self.map]
        return [key for key in keys if key.startswith(prefix)]

    def getAll(self, prefix=""):
        keys = self.getKeys(prefix)
        return {key: self.get(key) for key in keys}

    def put(self, key: str, value: Union[list, dict]):
        raise NotImplementedError(f"Writing to FileStore {self.path} is not supported")
