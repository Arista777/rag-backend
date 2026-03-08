import json
from pathlib import Path

import faiss
import numpy as np
from openai import OpenAI


class VectorStore:
    def __init__(
        self,
        client: OpenAI,
        embedding_model: str,
        index_path: Path,
        meta_path: Path,
    ) -> None:
        self.client = client
        self.embedding_model = embedding_model
        self.index_path = index_path
        self.meta_path = meta_path

        self.dimension = 1536
        self.index = self._load_or_create_index()
        self.metadata = self._load_metadata()

    def _load_or_create_index(self):
        if self.index_path.exists():
            return faiss.read_index(str(self.index_path))
        return faiss.IndexFlatL2(self.dimension)

    def _load_metadata(self) -> list[dict]:
        if not self.meta_path.exists():
            return []
        return json.loads(self.meta_path.read_text())

    def _save(self) -> None:
        faiss.write_index(self.index, str(self.index_path))
        self.meta_path.write_text(json.dumps(self.metadata, ensure_ascii=True, indent=2))

    def _embed(self, texts: list[str]) -> np.ndarray:
        response = self.client.embeddings.create(model=self.embedding_model, input=texts)
        vectors = [row.embedding for row in response.data]
        return np.array(vectors, dtype="float32")

    def add_texts(self, texts: list[str], metadata: list[dict]) -> int:
        if not texts:
            return 0

        vectors = self._embed(texts)
        self.index.add(vectors)
        self.metadata.extend(metadata)
        self._save()
        return len(texts)

    def search(self, query: str, k: int = 4) -> list[dict]:
        if self.index.ntotal == 0:
            return []

        query_vec = self._embed([query])
        _, indices = self.index.search(query_vec, min(k, self.index.ntotal))

        results: list[dict] = []
        for idx in indices[0]:
            if idx == -1:
                continue
            if idx < len(self.metadata):
                results.append(self.metadata[idx])
        return results
