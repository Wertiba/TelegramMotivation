import os

from dotenv import load_dotenv, find_dotenv
from gigachat import GigaChat
from src.services.singleton import singleton
from src.AI.llm_client import LLMClient


@singleton
class GigaClient(LLMClient):
    def __init__(self):
        super().__init__()
        load_dotenv(find_dotenv())
        self.key = os.getenv("GIGA_KEY")

    def process_prompt(self, idusers, content):
        try:
            message = self.get_message(content, idusers)
            prompt = "\n".join([m["content"] for m in message if "content" in m])
            with GigaChat(credentials=self.key, verify_ssl_certs=False) as giga:
                response = giga.chat(prompt).choices[0].message.content
                return response

        except Exception as e:
            self.logger.error(f"Error while Gigachat processing request: {e}")
