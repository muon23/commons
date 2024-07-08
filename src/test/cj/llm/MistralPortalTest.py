import asyncio
import os
import unittest

from cjutil.llm.ChatPrompt import ChatPrompt
from cjutil.llm.MistralPortal import MistralPortal


class MistralPortalTest(unittest.TestCase):
    def test_basic(self):
        key = os.environ["MISTRAL_API_KEY"]
        mistral = MistralPortal.of(key=key)

        prompt = ChatPrompt(bot="assistant")
        prompt.user("What models does MistralAI support?")

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(mistral.chatCompletion(messages=prompt.messages, model="mistral-medium"))

        print(result["content"])

        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
