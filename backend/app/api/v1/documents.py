from pathlib import Path
import uuid

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

    content = await file.read()
    size_bytes = len(content)
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max allowed size is {settings.max_upload_mb} MB",
        )

    safe_filename = file.filename or f"upload-{uuid.uuid4()}{suffix}"
    target_path = settings.upload_dir / safe_filename
    if target_path.exists():
        target_path = settings.upload_dir / f"{uuid.uuid4()}-{safe_filename}"
    target_path.write_bytes(content)

    text = DocumentService.extract_text(target_path)
    chunks = DocumentService.split(
        text,
        chunk_size=settings.max_chunk_size,
        overlap=settings.chunk_overlap,
    )

    if not chunks:
        raise HTTPException(status_code=400, detail="No extractable content in file")
    if len(chunks) > settings.max_chunks_per_upload:
        raise HTTPException(
            status_code=413,
            detail=(
                "Document produced too many chunks. "
                f"Max allowed is {settings.max_chunks_per_upload}; please split the file."
            ),
        )

    metadata = [
        {
            "text": chunk,
            "source_file": safe_filename,
            "chunk_index": idx,
        }
        for idx, chunk in enumerate(chunks)
    ]

    try:
        added = rag.vector_store.add_texts(
            chunks, metadata, batch_size=settings.embedding_batch_size
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Embedding failed: {exc}") from exc

    DocumentService.save_chunks(db, safe_filename, chunks)

    return UploadResponse(filename=safe_filename, chunks_added=added, status="ok")
