import os
from dotenv import load_dotenv, find_dotenv
from src.services.DB.storage import Storage
from src.services.ollama.ollama_client import OllamaClient
from src.services.ollama.ollama_settings import url, model
from src.services.DB.database_config import charset, port

load_dotenv(find_dotenv())
gemini = OllamaClient(url, model)
storage = Storage(os.getenv('DB_HOST'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'), os.getenv('DB_NAME'), port, charset)

while True:
    request = str(input('введите запрос: '))
    storage.save_request(1, 'user', request)
    answer = gemini.process_prompt(1, request)
    print(answer + '\n')
