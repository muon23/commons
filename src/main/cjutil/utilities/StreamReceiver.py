from abc import ABC, abstractmethod
from typing import TypeVar, Callable, Any


class StreamReceiver(ABC):
    StreamReceiver = TypeVar("StreamReceiver")

    @staticmethod
    def of(spec: str, callback=Callable[[Any], None]) -> StreamReceiver:
        if spec.startswith("amqp:") or spec.startswith("amqps:"):
            from cjutil.utilities.RabbitMQReceiver import RabbitMQReceiver
            return RabbitMQReceiver(spec, callback)
        else:
            raise NotImplementedError(f"Unsupported scheme from URI {spec}")

    @abstractmethod
    def receiving(self):
        pass



