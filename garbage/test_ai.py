from openai import OpenAI

key = ''
client = OpenAI(api_key=key)

response = client.responses.create(
  model="gpt-4.1",
  input="Tell me a three sentence bedtime story about a unicorn."
)

print(response)