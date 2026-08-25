## Groq client setup + ask_llm()

from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def ask_llm(user_query: str, system_prompt: str = "You are a helpful assistant"):
    response = client.chat.completions.create(
        model='openai/gpt-oss-20b',
        messages=[
            {'role':'user', 'content': user_query},
            {'role': 'system', 'content':system_prompt}
        ]
    )
    return response.choices[0].message.content