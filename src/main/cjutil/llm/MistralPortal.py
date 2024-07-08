import logging
from typing import List

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage


class MistralPortal:
    logger = logging.getLogger(__qualname__)  # Logger for logging messages

    __DEFAULT_MODEL = "mistral-tiny"

    @classmethod
    def of(cls, key: str, **kwargs) -> "MistralPortal":
        return MistralPortal(key, **kwargs)

    def __init__(self, key: str = None, model: str = None, **kwargs):
        self.mistral = MistralClient(api_key=key, **kwargs)
        self.model = model or self.__DEFAULT_MODEL

    async def chatCompletion(self, messages: List[dict], model=None, **kwargs) -> List[dict] | dict:
        messages = [ChatMessage(role=m["role"], content=m["content"]) for m in messages]
        multiple = kwargs.get("top_p", 1) > 1

        chat_response = self.mistral.chat(
            model=model or self.model,
            messages=messages,
            **kwargs
        )

        results = []
        for choice in chat_response.choices:
            results.append({
                "role": choice.message.role,
                "content": choice.message.content,
                "finish_reason": choice.finish_reason.name
            })

        return results if multiple else results[0]


