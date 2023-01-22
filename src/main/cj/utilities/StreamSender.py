from abc import ABC, abstractmethod
from typing import Any, TypeVar


class StreamSender(ABC):
    StreamSender = TypeVar("StreamSender")

    @staticmethod
    def of(spec: str) -> StreamSender:
        if spec.startswith("amqp:") or spec.startswith("amqps:"):
            from cj.utilities.RabbitMQSender import RabbitMQSender
            return RabbitMQSender(spec)
        else:
            raise NotImplementedError(f"Unsupported scheme from URI {spec}")

    @abstractmethod
    def send(self, message: Any):
        pass
