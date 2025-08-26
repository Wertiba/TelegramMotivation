import requests
import json

from settings.ollama_settings import temperarure
from src.services.singleton import singleton
from src.AI.llm_client import LLMClient

@singleton
class OllamaClient(LLMClient):
    def __init__(self, url, model):
        super().__init__()
        self.url = url
        self.model = model

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
            return self.strip_think_blocks(result)
        else:
            self.logger.error(f"Error while processing ollama request: {response.status_code} status code: {response.text}")
