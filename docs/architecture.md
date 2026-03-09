# Architecture

## High-level

- `frontend` (React + Tailwind): user interaction layer.
- `backend` (FastAPI): orchestration/API layer.
- `FAISS` local index: vector retrieval layer.
- `SQLite`: persistent state for chats/messages/document chunks.
- `OpenAI API`: LLM + embeddings.

## Backend module layout

- `app/core`: config and logging.
- `app/db`: SQLAlchemy setup and session.
- `app/models`: persistent entities.
- `app/schemas`: API contracts.
- `app/services`: RAG, chat, documents, vector store.
- `app/api`: routers and dependency wiring.

## Request flow

1. User sends message from frontend.
2. Backend persists user message in SQLite.
3. RAG service retrieves nearest chunks from FAISS.
4. Backend calls OpenAI Chat Completions with history + context.
5. Streaming tokens are sent back to frontend.
6. Final assistant message is persisted in SQLite.

## Document ingestion flow

1. User uploads PDF/TXT/MD.
2. Backend extracts text.
3. Text is chunked.
4. Chunks are embedded via OpenAI embeddings.
5. Vectors are added to FAISS, metadata persisted.
6. Chunk records are stored in SQLite.
