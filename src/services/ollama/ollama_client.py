import requests
import json
import os

from dotenv import load_dotenv, find_dotenv
from src.services.ollama.ollama_settings import system_prompt, temperarure, few_shot
from src.services.DB.storage import Storage
from src.logger import Logger
from src.services.DB.database_config import charset, autocommit


class OllamaClient:
    def __init__(self, url, model):
        load_dotenv(find_dotenv())
        self.url = url
        self.model = model
        self.logger = Logger()
        self.storage = Storage()

    def get_history(self, idusers):
        history = list()
        response = self.storage.get_user_history(idusers)

        for prompt in response:
            role, content = prompt
            history.append({"role": role, "content": content})
        return history

    def get_message(self, content, idusers):
        history = self.get_history(idusers)
        user_prompt = {"role": "user", "content": content}
        message = [system_prompt] + few_shot + history + [user_prompt]
        return message

    def process_prompt(self, idusers, content):
        message = self.get_message(content, idusers)
        payload = {
            "model": self.model,
            "messages": message,
            'temperature': temperarure
        }

        response = requests.post(self.url, json=payload, stream=True)

        if response.status_code == 200:
            result = ''
            for line in response.iter_lines(decode_unicode=True):
                if line:  # Ignore empty lines
                    try:
                        json_data = json.loads(line)
                        # Extract the assistant's message content
                        if "message" in json_data and "content" in json_data["message"]:
                            result += json_data["message"]["content"]
                    except json.JSONDecodeError:
                        self.logger.error(f"Error while processing ollama request: failed to parse line: {line}")

            self.storage.save_request(idusers, 'assistant', result)
            return result
        else:
            self.logger.error(f"Error while processing ollama request: {response.status_code} status code: {response.text}")
