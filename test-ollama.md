## How to test Ollama

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3:8b",
    "messages": [
      {
        "role": "user",
        "content": "Why is the sky blue?"
      }
    ]
  }'

  ```

  ### Replace the localhost URL with your Ollama server URL if it's running on a different host or port.

  ```bash
curl http://103.48.43.25:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1",
    "messages": [
      {
        "role": "user",
        "content": "Why is the sky blue?"
      }
    ]
  }'

  ```

## How to test Ollama with Python

```python

client = OpenAI(base_url="http://localhost:11434/v1",
    api_key="ollama")

response = client.chat.completions.create(
    model="llama3:8b",
    messages=[
        {
            "role": "user",
            "content": "Why is the sky blue?"
        }
    ]
)

print(response)
```