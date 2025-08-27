import os
import requests
import uuid

from dotenv import load_dotenv, find_dotenv
from gigachat import GigaChat
from settings.llm_settings import URL, MODEL, MAX_TOKENS, TEMPERATURE, REPETITION_PENALTY, UPDATE_INTERVAL, ANSWERS_QUANTITY, STREAM
from src.services.singleton import singleton
from src.LLM.llm_client import LLMClient


@singleton
class GigaClient(LLMClient):
    def __init__(self):
        super().__init__()
        load_dotenv(find_dotenv())
        self.key = os.getenv("GIGA_KEY")
        self.giga = GigaChat(credentials=self.key, )

    def process_prompt(self, idusers, content):
        try:
            token = self.giga.get_token().access_token
            prompt = self.get_message(content, idusers)

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "RqUID": str(uuid.uuid4()),
            }
            body = {
                "model": MODEL,
                "messages": prompt,
                "temperature": TEMPERATURE,
                "n": ANSWERS_QUANTITY,
                "stream": STREAM,
                "max_tokens": MAX_TOKENS,
                "repetition_penalty": REPETITION_PENALTY,
                "update_interval": UPDATE_INTERVAL
            }

            resp = requests.post(URL, json=body, headers=headers, verify=True)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

        except Exception as e:
            self.logger.error(f"Error while Gigachat processing request: {e}")
