import json
import logging
import pickle
from urllib.parse import urlparse

import javaobj as javaobj
import redis

from cj.utilities.KeyValueStore import KeyValueStore


class RedisStore(KeyValueStore):

    def __init__(
            self,
            uri: str,
            collection="",
            storageFormat="pickle",
            **kwargs
    ):
        url = urlparse(uri)

        self.host = url.hostname if url.hostname else "localhost"
        self.port = url.port if url.port else 6379
        self.password = url.password
        self.format = storageFormat
        self.collection = collection

        logging.info(f"Accessing Redis {self.host}:{self.port}, data format in {self.format}")
        self.redis = redis.Redis(self.host, self.port, self.password)

    def __makeKey(self, key):
        return f"{self.collection}:{key}"

    def exists(self, key: any):
        return self.redis.exists(self.__makeKey(key))

    def get(self, key: any):
        data = self.redis[self.__makeKey(key)]
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
        return len(self.redis.scan_iter(self.collection + "*"))

    def getName(self):
        return f"Redis({self.host},{self.port})"

    def getKeys(self):
        return [
            key.decode("utf-8").lstrip(f"{self.collection}:")
            for key in self.redis.scan_iter(self.collection + "*")
        ]

    def getAll(self):
        keys = [key.decode("utf-8") for key in self.redis.scan_iter(self.collection + "*")]
        kv = zip(keys, self.redis.mget(keys))
        if self.format == "javaobj":
            return {k: javaobj.loads(v) for k, v in kv}
        elif self.format == "pickle":
            return {k: pickle.loads(v) for k, v in kv}
        elif self.format == "json":
            return {k: json.loads(v) for k, v in kv}
        else:
            raise NotImplementedError(f"Unsupported value format {self.format} for getAll()")

    def put(self, key: any, value: any):
        kk = self.__makeKey(key)
        if self.format == "json":
            self.redis[kk] = json.dumps(value)
        elif self.format == "pickle":
            self.redis[kk] = pickle.dumps(value)
        else:
            raise NotImplementedError(f"Unsupported value format {self.format} for put()")

