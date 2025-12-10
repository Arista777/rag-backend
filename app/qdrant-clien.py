import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION")
