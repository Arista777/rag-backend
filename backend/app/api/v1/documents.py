from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_rag_service
from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.document import UploadResponse
from app.services.document_service import DocumentService
from app.services.rag_service import RAGService


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    rag: RAGService = Depends(get_rag_service),
):
    settings = get_settings()
    suffix = Path(file.filename).suffix.lower()

    if suffix not in {".pdf", ".txt", ".md"}:
        raise HTTPException(status_code=400, detail="Only .pdf, .txt and .md are supported")

    target_path = settings.upload_dir / file.filename
    target_path.write_bytes(await file.read())

    text = DocumentService.extract_text(target_path)
    chunks = DocumentService.split(
        text,
        chunk_size=settings.max_chunk_size,
        overlap=settings.chunk_overlap,
    )

    if not chunks:
        raise HTTPException(status_code=400, detail="No extractable content in file")

    metadata = [
        {
            "text": chunk,
            "source_file": file.filename,
            "chunk_index": idx,
        }
        for idx, chunk in enumerate(chunks)
    ]

    added = rag.vector_store.add_texts(chunks, metadata)
    DocumentService.save_chunks(db, file.filename, chunks)

    return UploadResponse(filename=file.filename, chunks_added=added, status="ok")
