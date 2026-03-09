from collections.abc import Generator
from datetime import datetime

from openai import OpenAI

from app.core.config import get_settings
from app.services.vector_store import VectorStore


class RAGService:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.vector_store = VectorStore(
            client=self.client,
            embedding_model=settings.openai_embedding_model,
            index_path=settings.vector_index_path,
            meta_path=settings.vector_meta_path,
        )

    def retrieve_context(self, query: str) -> tuple[str, list[dict]]:
        docs = self.vector_store.search(query, k=self.settings.retrieval_k)

        # Lexical fallback: improves recall when embeddings are weak for broad queries.
        query_terms = {term.strip(".,;:!?()[]{}\"'").lower() for term in query.split() if term}
        lexical_scored: list[tuple[int, dict]] = []
        if query_terms and self.vector_store.metadata:
            for item in self.vector_store.metadata[-5000:]:
                text = (item.get("text") or "").lower()
                score = sum(1 for term in query_terms if len(term) > 2 and term in text)
                if score > 0:
                    lexical_scored.append((score, item))
            lexical_scored.sort(key=lambda x: x[0], reverse=True)

        merged: list[dict] = []
        seen = set()
        for doc in docs + [item for _, item in lexical_scored[: self.settings.retrieval_k]]:
            key = (doc.get("source_file"), doc.get("chunk_index"))
            if key in seen:
                continue
            seen.add(key)
            merged.append(doc)
            if len(merged) >= self.settings.retrieval_k:
                break

        context = "\n\n".join(d.get("text", "") for d in merged)
        return context, merged

    def _is_document_query(self, user_input: str) -> bool:
        text = user_input.lower()
        keywords = [
            "documento",
            "document",
            "archivo",
            "pdf",
            "txt",
            "md",
            "segun el documento",
            "según el documento",
            "del documento",
            "uploaded file",
            "source file",
            "en el archivo",
            "archivo cargado",
            "documento cargado",
            "subi",
            "subí",
            "upload",
            "uploaded",
        ]
        return any(keyword in text for keyword in keywords)

    def _build_messages(
        self,
        user_input: str,
        history: list[dict],
        context: str,
        document_query: bool,
    ):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        system_prompt = (
            "You are a production AI assistant. "
            "Answer in the same language as the user. "
            f"Today (UTC) is {today}. "
            "For general questions, answer normally with your own knowledge."
        )
        if document_query:
            system_prompt += (
                " The user is asking about uploaded documents. "
                "Use retrieved context directly and do not claim you cannot read files or tools. "
                "If context is missing or insufficient, say exactly: "
                "'No encontré evidencia suficiente en los documentos cargados para responder con precisión.'"
            )

        messages = [{"role": "system", "content": system_prompt}]

        if context:
            messages.append(
                {
                    "role": "system",
                    "content": f"Retrieved context:\n{context}",
                }
            )

        messages.extend(history[-10:])
        messages.append({"role": "user", "content": user_input})
        return messages

    def generate_answer(self, user_input: str, history: list[dict]) -> tuple[str, list[dict]]:
        document_query = self._is_document_query(user_input)
        context, sources = ("", [])
        if document_query:
            context, sources = self.retrieve_context(user_input)
        messages = self._build_messages(user_input, history, context, document_query)

        response = self.client.chat.completions.create(
            model=self.settings.openai_chat_model,
            messages=messages,
            temperature=0.3,
        )
        text = response.choices[0].message.content or ""
        return text, sources

    def stream_answer(self, user_input: str, history: list[dict]) -> tuple[Generator[str, None, None], list[dict]]:
        document_query = self._is_document_query(user_input)
        context, sources = ("", [])
        if document_query:
            context, sources = self.retrieve_context(user_input)
        messages = self._build_messages(user_input, history, context, document_query)

        stream = self.client.chat.completions.create(
            model=self.settings.openai_chat_model,
            messages=messages,
            temperature=0.3,
            stream=True,
        )

        def token_generator() -> Generator[str, None, None]:
            for chunk in stream:
                token = chunk.choices[0].delta.content if chunk.choices else None
                if token:
                    yield token

        return token_generator(), sources
