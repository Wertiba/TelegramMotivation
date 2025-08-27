import os
import re

from dotenv import load_dotenv, find_dotenv
from settings.config import charset, port
from settings.llm_settings import SYSTEM_PROMPT
from src.DB.storage import Storage
from src.services.logger import Logger


class LLMClient:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.logger = Logger().get_logger()
        self.storage = Storage(os.getenv('DB_HOST'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'), os.getenv('DB_NAME'), charset, port=port)

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
        message = [SYSTEM_PROMPT] + language_prompt + memory_prompt + user_prompt
        return message
