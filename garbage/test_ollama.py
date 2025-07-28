import requests
import json

# Set up the base URL for the local Ollama API
url = "http://localhost:11434/api/chat"

# 1. Системный промпт — поведение модели
system_prompt = {
    "role": "system",
    "content": "Ты — дружелюбный и полезный русскоязычный помощник. Отвечай понятно и кратко."
}

# 2. Индивидуальные характеристики пользователя (например, из базы)
memory_prompt = {
    "role": "system",
    "name": "memory",  # можно опустить, если модель не поддерживает именные роли
    "content": "Пользователь дружелюбный собеседник, но любит краткость в сообщениях"
}

# 3. История диалога
history = [
    {"role": "user", "content": "Привет!"},
    {"role": "assistant", "content": "Привет! Чем могу помочь?"},
    {"role": "user", "content": "Меня зовут Егор"},
    {"role": "assistant", "content": "Приятно познакомиться!"}
]

# 4. Новый запрос
# (можно добавить на лету, или оставить `history[-1]` как актуальный ввод)
user_input = {"role": "user", "content": "как меня зовут?"}

# 5. Финальный список сообщений
messages = [system_prompt, memory_prompt] + history + [user_input]
# Define the payload (your input prompt)
payload = {
    "model": "gemma3:1b",  # Replace with the model name you're using
    "messages": messages,
    'temperature': 0.75
}

# Send the HTTP POST request with streaming enabled
response = requests.post(url, json=payload, stream=True)

# Check the response status
if response.status_code == 200:
    print("Streaming response from Ollama:")
    for line in response.iter_lines(decode_unicode=True):
        if line:  # Ignore empty lines
            try:
                # Parse each line as a JSON object
                json_data = json.loads(line)
                # Extract and print the assistant's message content
                if "message" in json_data and "content" in json_data["message"]:
                    print(json_data["message"]["content"], end="")
            except json.JSONDecodeError:
                print(f"\nFailed to parse line: {line}")
    print()  # Ensure the final output ends with a newline
else:
    print(f"Error: {response.status_code}")
    print(response.text)
