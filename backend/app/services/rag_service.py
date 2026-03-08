from collections.abc import Generator

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
        context = "\n\n".join(d.get("text", "") for d in docs)
        return context, docs

    def _build_messages(self, user_input: str, history: list[dict], context: str):
        system_prompt = (
            "You are a production AI assistant. Answer clearly and concisely. "
            "Use retrieved context when relevant. If context is insufficient, say so explicitly."
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
        context, sources = self.retrieve_context(user_input)
        messages = self._build_messages(user_input, history, context)

        response = self.client.chat.completions.create(
            model=self.settings.openai_chat_model,
            messages=messages,
            temperature=0.3,
        )
        text = response.choices[0].message.content or ""
        return text, sources

    def stream_answer(self, user_input: str, history: list[dict]) -> tuple[Generator[str, None, None], list[dict]]:
        context, sources = self.retrieve_context(user_input)
        messages = self._build_messages(user_input, history, context)

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
