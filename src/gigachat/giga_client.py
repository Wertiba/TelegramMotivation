import os
import re

from dotenv import load_dotenv, find_dotenv
from gigachat import GigaChat
from settings.config import charset, port
from settings.ollama_settings import system_prompt, temperarure, few_shot
from src.DB.storage import Storage
from src.services.logger import Logger
from src.services.singleton import singleton


@singleton
class GigaClient:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.key = os.getenv("GIGA_KEY")
        self.logger = Logger().get_logger()
        self.storage = Storage(os.getenv('DB_HOST'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'),
                               os.getenv('DB_NAME'), charset, port=port)

    def get_history(self, idusers):
        history = list()
        response = self.storage.get_user_history(idusers)

        for prompt in response:
            role, content = prompt
            history.append({"role": role, "content": content})
        return history

    def strip_think_blocks(self, text):
        return re.sub(r"<think>.*?</think>\s*", "", text, flags=re.DOTALL)

    def get_message(self, content, idusers):
        memory_content = self.storage.get_memory_prompt(idusers)
        language = self.storage.get_language(idusers)
        # history = self.get_history(idusers)
        memory_prompt = [{"role": "user_info", "content": memory_content[0]}] if memory_content and memory_content[0] else list()
        language_prompt = [{"role": "system", "name": "language", "content": language[0][0]}] if language and language[0] else list()
        user_prompt = [{"role": "user", "content": content}]
        message = [system_prompt] + language_prompt + memory_prompt + user_prompt
        return message

    def process_prompt(self, idusers, content):
        try:
            message = self.get_message(content, idusers)
            prompt = "\n".join([m["content"] for m in message if "content" in m])
            with GigaChat(credentials=self.key, verify_ssl_certs=False) as giga:
                response = giga.chat(prompt).choices[0].message.content
                return response

        except Exception as e:
            self.logger.error(f"Error while Gigachat processing request: {e}")
