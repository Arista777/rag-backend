import numpy as np
import faiss
import tiktoken
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def embed_texts(texts):
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=texts
    )
    vectors = [d.embedding for d in response.data]
    return np.array(vectors).astype("float32")
