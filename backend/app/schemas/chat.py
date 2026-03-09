from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ChatCreate(BaseModel):
    title: str | None = None


class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    content: str
    stream: bool = True


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chat_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime


class ChatWithMessages(BaseModel):
    chat: ChatResponse
    messages: list[MessageResponse]
