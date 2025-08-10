import os
from dotenv import load_dotenv, find_dotenv
from src.DB.storage import Storage
from src.ollama.ollama_client import OllamaClient
from settings.ollama_settings import url, model
from settings.database_config import charset, port

load_dotenv(find_dotenv())
gemini = OllamaClient(url, model)
storage = Storage(os.getenv('DB_HOST'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'), os.getenv('DB_NAME'), charset, port=port)

while True:
    request = str(input('введите запрос: '))
    storage.save_request(1, 'user', request)
    answer = gemini.process_prompt(1, request)
    print(answer + '\n')
