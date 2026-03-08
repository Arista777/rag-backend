# AI Assistant (ChatGPT-style) - Production Ready Refactor

This repository has been refactored into a production-oriented full-stack AI assistant with:

- FastAPI backend
- React + Tailwind frontend
- RAG document ingestion/retrieval with FAISS
- OpenAI chat completion integration
- Persistent chat history (SQLite)
- Dockerized local deployment
- AWS deployment documentation

## Project structure

```text
/project
  /backend        # FastAPI app, RAG pipeline, chat and document APIs
  /frontend       # React + Tailwind chat interface
  /docker         # Dockerfiles + nginx config
  /docs           # Deployment documentation
  docker-compose.yml
```

## Backend features

- REST API under `/api/v1`
- Chat endpoints with conversation memory
- Streaming assistant responses (`text/event-stream`)
- Document upload (`.pdf`, `.txt`, `.md`)
- Chunking + embedding + FAISS indexing
- SQLite persistence for chats/messages/document chunks

Main endpoints:

- `GET /api/v1/health`
- `GET /api/v1/chats`
- `POST /api/v1/chats`
- `GET /api/v1/chats/{chat_id}/messages`
- `POST /api/v1/chats/{chat_id}/messages`
- `POST /api/v1/documents/upload`

## Frontend features

- ChatGPT-style split layout (sidebar + chat pane)
- Conversation history sidebar
- Streaming message rendering
- Document upload UI
- Responsive Tailwind styling

## Local development

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm start
```

Frontend runs on `http://localhost:3000` and backend on `http://localhost:8000`.

## Docker deployment (local)

1. Create backend env file:

```bash
cp backend/.env.example backend/.env
```

2. Run containers:

```bash
docker compose up --build
```

## Environment variables

Backend (`backend/.env`):

- `OPENAI_API_KEY`
- `OPENAI_CHAT_MODEL` (default: `gpt-4o-mini`)
- `OPENAI_EMBEDDING_MODEL` (default: `text-embedding-3-small`)
- `ALLOWED_ORIGINS` (default: `http://localhost:3000`)

Frontend (`frontend/.env`):

- `REACT_APP_API_URL` (default: `http://localhost:8000/api/v1`)

## AWS deployment

See full guide in [docs/aws-deployment.md](docs/aws-deployment.md).

## Code quality improvements applied

- Modular backend architecture (`api`, `services`, `models`, `schemas`, `core`)
- Strong separation of concerns
- Centralized configuration
- Robust error handling and explicit HTTP responses
- Logging setup for production observability
- Clean frontend component/hook API boundaries
