import requests
import json

from src.servicies.ollama.ollama_settings import system_prompt, memory_prompt, temperarure
from src.servicies.DB.storage import Storage
from src.logger import Logger


class OllamaClient:
    def __init__(self, url, model):
        self.url = url
        self.model = model
        self.storage = Storage()
        self.logger = Logger()

    def get_message(self, content):
        history = self.storage.get_user_history(None)
        promt = {"role": "user", "content": content}
        message = [system_prompt, memory_prompt] + history + [promt] if history else [system_prompt, memory_prompt] + [promt]
        return message

    def process_prompt(self, promt):
        message = self.get_message(promt)
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
            return result
        else:
            self.logger.error(f"Error while processing ollama request: {response.status_code} status code: {response.text}")
