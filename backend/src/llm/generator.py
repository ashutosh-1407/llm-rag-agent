from openai import OpenAI
from backend.src.utils.constants import OPENAI_MODEL_NAME
import os


client = OpenAI(api_key=os.getenv("OPENAI_APIK_KEY"))

def generate_completion(messages, tools=None, tools_choice="auto", temperature=0):
    kwargs = {
        "model": OPENAI_MODEL_NAME,
        "messages": messages,
        "temperature": temperature
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = tools_choice
    response = client.chat.completions.create(**kwargs)
    return response
