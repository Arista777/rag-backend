import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chat import ChatCreate, ChatResponse, MessageCreate, MessageResponse
from app.services.chat_service import ChatService
from app.services.rag_service import RAGService
from app.api.deps import get_rag_service


router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("", response_model=list[ChatResponse])
def list_chats(db: Session = Depends(get_db)):
    return ChatService.list_chats(db)


@router.post("", response_model=ChatResponse)
def create_chat(payload: ChatCreate, db: Session = Depends(get_db)):
    return ChatService.create_chat(db, payload.title)


@router.get("/{chat_id}/messages", response_model=list[MessageResponse])
def list_messages(chat_id: str, db: Session = Depends(get_db)):
    chat = ChatService.get_chat(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return ChatService.get_messages(db, chat_id)


@router.post("/{chat_id}/messages")
def create_message(
    chat_id: str,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    rag: RAGService = Depends(get_rag_service),
):
    chat = ChatService.get_chat(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    ChatService.add_message(db, chat_id=chat_id, role="user", content=payload.content)
    history = ChatService.as_llm_history(ChatService.get_messages(db, chat_id))

    if payload.stream:
        token_stream, sources = rag.stream_answer(payload.content, history)

        def event_generator():
            full = ""
            for token in token_stream:
                full += token
                yield f"data: {json.dumps({'type': 'token', 'value': token})}\n\n"
            ChatService.add_message(db, chat_id=chat_id, role="assistant", content=full)
            yield f"data: {json.dumps({'type': 'done', 'sources': sources})}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    answer, sources = rag.generate_answer(payload.content, history)
    message = ChatService.add_message(db, chat_id=chat_id, role="assistant", content=answer)
    return {"message": MessageResponse.model_validate(message).model_dump(), "sources": sources}
