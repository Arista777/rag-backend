# app/rag.py
import os
from openai import OpenAI

class RAG:
    def __init__(self, qdrant=None, collection_name="default"):
        self.qdrant = qdrant
        self.collection_name = collection_name
        self.docs = []

        # Cliente OpenAI
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def add_document(self, text, filename):
        self.docs.append({"text": text, "filename": filename})
        if self.qdrant:
            import uuid
            vector = [0.0] * 1536
            point_id = str(uuid.uuid4())
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=[{
                    "id": point_id,
                    "vector": vector,
                    "payload": {
                        "text": text,
                        "filename": filename
                    }
                }]
            )
        return {"status": "ok", "filename": filename}

    def search(self, query, k=3):
        # Tomamos los últimos k documentos para contexto
        context = "\n".join([doc["text"] for doc in self.docs[-k:]])
        prompt = f"{context}\nPregunta: {query}\nRespuesta:"

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            answer = response.choices[0].message.content.strip()
        except Exception as e:
            answer = f"Error al generar respuesta: {e}"

        return [{"text": answer, "filename": None}]
