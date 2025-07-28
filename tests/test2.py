from src.servicies.ollama.ollama_client import OllamaClient
from src.servicies.ollama.ollama_settings import url, model

gemini = OllamaClient(url, model)
print(gemini.process_prompt('как меня зовут?'))
