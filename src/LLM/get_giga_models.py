import requests
import os
import uuid

from dotenv import load_dotenv, find_dotenv
from gigachat import GigaChat

load_dotenv(find_dotenv())
giga = GigaChat(credentials=os.getenv("GIGA_KEY"))
token = giga.get_token().access_token

def get_models():
    url = "https://gigachat.devices.sberbank.ru/api/v1/models"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
    }

    response = requests.get(url, headers=headers, verify=True)
    return response.json()

if __name__ == '__main__':
    print(get_models())
