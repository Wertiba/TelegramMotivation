import requests
import json
from config import token2


response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {token2}",
        "Content-Type": "application/json"
    },
    data=json.dumps({
        "model": "qwen/qwen3-235b-a22b-07-25:free",
        "messages": [
            {
                "role": "user",
                "content": "как дела?)"
            }
        ],

    })
)

print(json.loads(response.text)['choices'][0]['message']['content'])
