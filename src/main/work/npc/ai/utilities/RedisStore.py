from typing import Union

import javaobj.v2 as javaobj
import json
import redis

from work.npc.ai.utilities.KeyValueStore import KeyValueStore


class RedisStore(KeyValueStore):

    def __init__(self, args):
        self.host = args[0] if len(args) > 0 else "localhost"
        self.port = int(args[1]) if len(args) > 1 else 6379
        self.password = args[2] if len(args) > 2 else ""
        self.redis = redis.Redis(self.host, self.port, self.password)

    def exists(self, key: str):
        return self.redis.exists(key)

    def get(self, key: str, valueFormat: str = "javaobj"):
        data = self.redis[key]
        if valueFormat == "javaobj":
            return javaobj.loads(data)
        elif valueFormat == "json":
            return json.loads(data)

    def getName(self):
        return f"Redis({self.host},{self.port})"

    def getKeys(self, prefix=""):
        return [key.decode("utf-8") for key in self.redis.scan_iter(prefix + "*")]

    def getAll(self, prefix=""):
        keys = self.getKeys(prefix)
        return {k: javaobj.loads(v) for k, v in zip(keys, self.redis.mget(keys))}

    def put(self, key: str, value: Union[list, dict]):
        self.redis[key] = json.dumps(value)

