import json
import pickle

import javaobj.v2 as javaobj
import redis

from work.npc.ai.utilities.KeyValueStore import KeyValueStore


class RedisStore(KeyValueStore):

    def __init__(self, args):
        self.host = args[0] if len(args) > 0 else "localhost"
        self.port = int(args[1]) if len(args) > 1 and args[1] else 6379
        self.password = args[2] if len(args) > 2 and args[2] else ""
        self.format = args[3] if len(args) > 3 and args[3] else "javaobj"
        self.redis = redis.Redis(self.host, self.port, self.password)

    def exists(self, key: str):
        return self.redis.exists(key)

    def get(self, key: str):
        data = self.redis[key]
        if self.format == "javaobj":
            return javaobj.loads(data)
        elif self.format == "json":
            return json.loads(data)
        elif self.format == "pickle":
            return pickle.loads(data)
        else:
            raise NotImplementedError(f"Unsupported value format {self.format} for get()")

    def flush(self):
        pass

    def getNumEntries(self):
        return len(self.redis.scan_iter())

    def getName(self):
        return f"Redis({self.host},{self.port})"

    def getKeys(self, prefix=""):
        return [key.decode("utf-8") for key in self.redis.scan_iter(prefix + "*")]

    def getAll(self, prefix=""):
        keys = self.getKeys(prefix)
        return {k: javaobj.loads(v) for k, v in zip(keys, self.redis.mget(keys))}

    def put(self, key: str, value: any):
        if self.format == "json":
            self.redis[key] = json.dumps(value)
        elif self.format == "pickle":
            self.redis[key] = pickle.dumps(value)
        else:
            raise NotImplementedError(f"Unsupported value format {self.format} for put()")

