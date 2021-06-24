from typing import Union

import javaobj.v2 as javaobj
import json

from work.npc.ai.utilities.KeyValueStore import KeyValueStore


class FileStore(KeyValueStore):

    def __init__(self, args):
        if not args:
            raise RuntimeError("Key-value store file name required")

        self.path = args[0]
        self.access = args[1] if len(args) > 1 and args[1] else "r"
        self.format = args[2] if len(args) > 2 and args[2] else "javaobj"
        self.output = args[3] if len(args) > 3 and args[3] else self.path
        self.updated = False

        self.access = "".join({c for c in self.access if c in "rwa"})

        if self.format == "javaobj":
            # Only read operation is supported
            if "w" in self.access or "a" in self.access:
                raise NotImplementedError(f"Writing Java object is not supported")

            with open(self.path, "rb") as fd:
                self.map = javaobj.load(fd)

        elif self.format == "json":
            if "w" in self.access:
                self.map = dict()
            else:
                with open(self.path, self.access) as fd:
                    self.map = json.load(fd)

        else:
            raise NotImplementedError(f"Format {self.format} not supported")

    def __del__(self):
        if self.updated and ("w" in self.access or "a" in self.access):
            assert self.format != "javaobj"  # Java object file cannot be writable from Python
            with open(self.path, "w") as fd:
                json.dump(self.map, fd)

    def exists(self, key):
        return key in self.map

    def get(self, key):
        if self.format == "javaobj":
            return javaobj.loads(bytes([x % 256 for x in self.map[key]]))
        elif self.format == "json":
            return json.loads(self.map[key])
        else:
            assert False  # will never be here

    def getName(self):
        return f"File({self.path})"

    def getKeys(self, prefix=""):
        keys = [str(key) for key in self.map]
        return [key for key in keys if key.startswith(prefix)]

    def getAll(self, prefix=""):
        keys = self.getKeys(prefix)
        return {key: self.get(key) for key in keys}

    def put(self, key: str, value: Union[list, dict]):
        if "w" not in self.access:
            raise RuntimeError(f"FileStore {self.path} is not writable")

        assert self.format != "javaobj"  # Java object file cannot be writable from Python
        self.map[key] = value
        self.updated = True


