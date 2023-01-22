import logging
import time
from asyncio import Lock
from typing import List

import openai
from transformers import GPT2TokenizerFast


class Gpt3Portal:

    class AuthenticationError(Exception):
        pass

    class ServiceNotAvailableError(Exception):
        pass

    class TooManyTokensError(Exception):
        pass

    __instance: "Gpt3Portal" = None
    __tokenizer = None

    @classmethod
    def of(cls, key: str) -> "Gpt3Portal":
        if not cls.__instance:
            cls.__instance = Gpt3Portal(key)
        return cls.__instance

    def __init__(self, key: str):
        try:
            openai.api_key = key
            self.__completion = openai.Completion()
        except Exception as e:
            raise RuntimeError(f"Cannot access GPT-3. {str(e)}")

        self.mutex = Lock()

    async def complete(self, prompt: str, retries: int = 1, **kwargs) -> List[str]:

        if "engine" not in kwargs:
            kwargs["engine"] = "text-davinci-003"

        response = None
        tries = 0
        while not response:
            try:
                async with self.mutex:
                    response = self.__completion.create(prompt=prompt, **kwargs)

                # response = response.choices[0].text.strip()
                response = [r.text.strip() for r in response.choices]

            except (
                openai.error.AuthenticationError,
                openai.error.APIError
            ) as e:
                raise self.AuthenticationError(f"GPT-3 key authentication failed.  {str(e)}")

            except (
                openai.error.APIConnectionError,
                openai.error.RateLimitError,
                openai.error.ServiceUnavailableError,
                openai.error.Timeout,
            ) as e:
                tries += 1
                if tries > retries:
                    raise self.ServiceNotAvailableError(f"GPT-3 access failed after {tries-1} tries.  Please try later")

                logging.warning(f"GPT-3 access failure (try {tries}).  {str(e)}")
                time.sleep(1)

            except openai.error.InvalidRequestError as e:
                message = f"GPT-3 token limit exceeds.  {str(e)}"
                logging.warning(message)
                raise self.TooManyTokensError(message)

        return response

    @classmethod
    def estimateTokens(cls, text: str) -> int:
        if not text:
            return 0
        if not cls.__tokenizer:
            cls.__tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

        return len(cls.__tokenizer(text)["input_ids"])
