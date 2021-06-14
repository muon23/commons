import javaobj.v2 as javaobj

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

    def get(self, key):
        return javaobj.loads(bytes([x % 256 for x in self.map[key]]))

    def getName(self):
        return f"File({self.path})"

    def getKeys(self, prefix=""):
        keys = [str(key) for key in self.map]
        return [key for key in keys if key.startswith(prefix)]

    def getAll(self, prefix=""):
        keys = self.getKeys(prefix)
        return {key: self.get(key) for key in keys}
