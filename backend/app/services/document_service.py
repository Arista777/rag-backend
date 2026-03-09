from pathlib import Path

from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.models.document import DocumentChunk
from app.utils.text import chunk_text


class DocumentService:
    @staticmethod
    def extract_text(file_path: Path) -> str:
        if file_path.suffix.lower() == ".pdf":
            reader = PdfReader(str(file_path))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        return file_path.read_text(encoding="utf-8", errors="ignore")

    @staticmethod
    def save_chunks(db: Session, filename: str, chunks: list[str]) -> None:
        records = [
            DocumentChunk(source_file=filename, chunk_index=idx, content=chunk)
            for idx, chunk in enumerate(chunks)
        ]
        db.add_all(records)
        db.commit()

    @staticmethod
    def split(text: str, chunk_size: int, overlap: int) -> list[str]:
        return chunk_text(text=text, chunk_size=chunk_size, overlap=overlap)
