import os
import re

from dotenv import load_dotenv, find_dotenv
from settings.config import charset, port
from settings.llm_settings import SYSTEM_PROMPT
from src.DB.storage import Storage
from src.services.logger import Logger


class LLMClient:
    def __init__(self):
        self.logger = Logger().get_logger()
        load_dotenv(find_dotenv())
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
        user_prompt = [{"role": "user", "content": content}]
        system_parts = [SYSTEM_PROMPT]
        # history = self.get_history(idusers)

        if language and language[0]:
            system_parts.append(f"Preferred language: {language[0][0]}")

        if memory_content and memory_content[0]:
            system_parts.append(f"User style/preferences: {memory_content[0]}")

        system_message = {
            "role": "system",
            "content": " | ".join(system_parts)
        }

        return [system_message] + user_prompt
