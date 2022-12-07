import logging
import time
from asyncio import Lock

import openai
from typing import List


class Gpt3Portal:

    __instance: "Gpt3Portal" = None

    @classmethod
    def of(cls, key: str) -> "Gpt3Portal":
        if not cls.__instance:
            cls.__instance = Gpt3Portal(key)
        return cls.__instance

    def __init__(self, key: str):
        try:
            openai.api_key = key
            self.completion = openai.Completion()
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
                    response = self.completion.create(prompt=prompt, **kwargs)

                # response = response.choices[0].text.strip()
                response = [r.text.strip() for r in response.choices]

            except openai.error.AuthenticationError as e:
                raise RuntimeError(f"GPT-3 key authentication failed.  {str(e)}")

            except (
                openai.error.APIConnectionError,
                openai.error.RateLimitError,
                openai.error.ServiceUnavailableError,
            ) as e:
                tries += 1
                if tries > retries:
                    raise RuntimeError(f"GPT-3 access failed after {tries} tries.  Please try later")

                logging.warning(f"GPT-3 access failure (try {tries}).  {str(e)}")
                time.sleep(1)

            except openai.error.InvalidRequestError as e:
                message = f"GPT-3 token limit exceeds.  {str(e)}"
                logging.warning(message)
                raise RuntimeError(message)

        return response

