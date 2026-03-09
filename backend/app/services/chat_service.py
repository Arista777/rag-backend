from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.chat import Chat, Message


class ChatService:
    @staticmethod
    def list_chats(db: Session) -> list[Chat]:
        return db.scalars(select(Chat).order_by(desc(Chat.updated_at))).all()

    @staticmethod
    def create_chat(db: Session, title: str | None = None) -> Chat:
        chat = Chat(title=title or "New Chat")
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat

    @staticmethod
    def get_chat(db: Session, chat_id: str) -> Chat | None:
        return db.get(Chat, chat_id)

    @staticmethod
    def add_message(db: Session, chat_id: str, role: str, content: str) -> Message:
        message = Message(chat_id=chat_id, role=role, content=content)
        db.add(message)

        chat = db.get(Chat, chat_id)
        if chat is not None:
            chat.updated_at = datetime.utcnow()
            if role == "user" and chat.title == "New Chat":
                chat.title = content[:40]

        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_messages(db: Session, chat_id: str) -> list[Message]:
        return db.scalars(
            select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at)
        ).all()

    @staticmethod
    def as_llm_history(messages: list[Message]) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in messages]
