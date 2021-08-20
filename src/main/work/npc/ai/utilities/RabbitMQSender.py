import pickle
from typing import Any
from urllib.parse import urlsplit, parse_qs

import json
import pika

from work.npc.ai.utilities.StreamSender import StreamSender


class RabbitMQSender(StreamSender):
    SUPPORTED_FORMAT = ["pickle", "json", "javaobj"]

    def __init__(self, spec: str):
        self.url = urlsplit(spec)

        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=self.url.hostname if self.url.hostname else "localhost",
            port=self.url.port if self.url.port else 5672
        ))
        self.channel = connection.channel()

        query = parse_qs(self.url.query)
        if "queue" not in query:
            raise ValueError(f"Queue name not found in {spec} (did you miss query component `?queue=...`?)")
        self.queue = query["queue"][0]
        self.channel.queue_declare(queue=self.queue)

        self.format = query.get("format", ["pickle"])[0]
        if self.format not in self.SUPPORTED_FORMAT:
            raise NotImplementedError(f"Unsupported serializing format {self.format}")

    def send(self, message: Any):
        if self.format == "pickle":
            body = pickle.dumps(message)
        elif self.format == "json":
            body = json.dumps(message)
        elif self.format == "javaobj":
            raise NotImplementedError(f"Sending Java object from Python is not supported")
        else:
            assert False  # will never be here

        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue,
            body=body
        )


