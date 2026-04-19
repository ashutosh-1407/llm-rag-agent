from openai import OpenAI
from backend.src.utils.constants import EMBEDDER_MODEL
import os
import numpy as np


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_text(text: str):
    response = client.embeddings.create(
        model=EMBEDDER_MODEL,
        input=text
    )
    response = [item.embedding for item in response.data]
    response = np.array(response).astype("float32")
    return response
