import os

from groq import Groq

client = Groq(
    api_key="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")

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama-3.2-11b-vision-preview",
)

print(chat_completion.choices[0].message.content)
