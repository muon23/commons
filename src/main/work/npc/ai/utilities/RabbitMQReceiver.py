import json
import pickle
from typing import Callable, Any
from urllib.parse import urlsplit, parse_qs

import javaobj
import pika

from work.npc.ai.utilities.StreamReceiver import StreamReceiver


class RabbitMQReceiver(StreamReceiver):
    SUPPORTED_FORMAT = ["pickle", "json", "javaobj"]

    def __init__(self, spec: str, callback: Callable[[Any], None]):
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

        self.callback = callback

        self.channel.basic_consume(
            queue=self.queue,
            auto_ack=True,
            on_message_callback=lambda ch, method, properties, body: self.__callback(body)
        )

    def receiving(self):
        self.channel.start_consuming()

    def __callback(self, body):
        if self.format == "javaobj":
            data = javaobj.loads(body)
        elif self.format == "pickle":
            data = pickle.loads(body)
        elif self.format == "json":
            data = json.loads(body)
        else:
            assert False  # Should not reach here

        self.callback(data)

