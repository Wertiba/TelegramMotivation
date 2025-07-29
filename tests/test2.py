import re
from src.servicies.ollama.ollama_client import OllamaClient
from src.servicies.ollama.ollama_settings import url, model
from src.servicies.DB.storage import Storage

gemini = OllamaClient(url, model)
storage = Storage()

def de_emojify(text):
    regrex_pattern = re.compile(pattern = "["
                                u"\U00000000-\U00000009"
                                u"\U0000000B-\U0000001F"
                                u"\U00000080-\U00000400"
                                u"\U00000402-\U0000040F"
                                u"\U00000450-\U00000450"
                                u"\U00000452-\U0010FFFF"
                                "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)

while True:
    request = str(input('введите запрос: '))
    storage.save_request(1, 'user', request)
    answer = gemini.process_prompt(request, 1)
    print(answer + '\n')

    storage.save_request(1, 'assistant', de_emojify(answer))
