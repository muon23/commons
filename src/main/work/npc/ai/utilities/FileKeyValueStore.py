import json
import os
import pickle

import javaobj.v2 as javaobj

from work.npc.ai.utilities.KeyValueStore import KeyValueStore


class FileKeyValueStore(KeyValueStore):

    def __init__(self, path, file, storageFormat=None, access="r"):
        if not path:
            raise RuntimeError("Key-value store file name required")

        self.path = os.path.join(path, file)
        self.access = access

        if storageFormat:
            self.format = storageFormat
            if storageFormat in ["json", "pickle"] and not self.path.endswith(storageFormat):
                self.path += f".{storageFormat}"
        elif self.path.endswith(".json"):
            self.format = "json"
        elif self.path.endswith(".pickle"):
            self.format = "pickle"
        else:
            self.format = "javaobj"

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
                try:
                    with open(self.path, self.access) as fd:
                        self.map = json.load(fd)
                except IOError:
                    self.map = dict()

        elif self.format == "pickle":
            if "w" in self.access:
                self.map = dict()
            else:
                try:
                    with open(self.path, self.access + "b") as fd:
                        self.map = pickle.load(fd)
                except IOError as e:
                    self.map = dict()

        else:
            raise NotImplementedError(f"Format {self.format} not supported")

    def __del__(self):
        self.flush()

    def flush(self):
        if self.updated and ("w" in self.access or "a" in self.access):
            assert self.format != "javaobj"  # Java object file cannot be writable from Python

            directory = os.path.dirname(self.path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            if self.format == "json":
                with open(self.path, "w") as fd:
                    json.dump(self.map, fd)

            elif self.format == "pickle":
                with open(self.path, "wb") as fd:
                    pickle.dump(self.map, fd)

            else:
                raise NotImplementedError(f"Format {self.format} not support for writing")

    def exists(self, key):
        return key in self.map

    def get(self, key):
        if self.format == "javaobj":
            return javaobj.loads(bytes([x % 256 for x in self.map[key]]))
        elif self.format == "json":
            return self.map[str(key)]
        elif self.format == "pickle":
            return self.map[key]
        else:
            assert False  # will never be here

    def getName(self):
        return f"File({self.path})"

    def getKeys(self):
        return list(self.map.keys())

    def getAll(self):
        return self.map

    def put(self, key: any, value: any):
        if "w" not in self.access:
            raise RuntimeError(f"FileStore {self.path} is not writable")

        assert self.format != "javaobj"  # Java object file cannot be writable from Python
        self.map[key] = value
        self.updated = True

    def getNumEntries(self):
        return len(self.map)


