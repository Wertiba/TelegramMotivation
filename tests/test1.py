from src.services.DB.storage import Storage
from src.services.ollama.ollama_client import OllamaClient
from src.services.ollama.ollama_settings import url, model
from tests.test2 import de_emojify

gemini = OllamaClient(url, model)
storage = Storage()

while True:
    request = de_emojify(str(input('введите запрос: ')))
    storage.save_request(1, 'user', request)
    answer = gemini.process_prompt(1, request)
    print(answer + '\n')
