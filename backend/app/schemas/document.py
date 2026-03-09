from pydantic import BaseModel


class UploadResponse(BaseModel):
    filename: str
    chunks_added: int
    status: str
