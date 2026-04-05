"""POST /api/v1/classify — single file classification."""
import asyncio
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.config import settings
from app.database import get_db
from app.models.db_models import Document
from app.models.schemas import ClassifyResponse, DOC_TYPE_LABELS
from app.services import ocr_service, classifier_service

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
ALLOWED_CONTENT_TYPES = {
    "image/jpeg", "image/jpg", "image/png", "application/pdf"
}


def _validate_file(file: UploadFile) -> None:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not supported. Use JPG, PNG, or PDF.",
        )


@router.post("", response_model=ClassifyResponse, status_code=200)
async def classify_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    _validate_file(file)

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="File is empty")

    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB",
        )

    ext = Path(file.filename or "file").suffix.lower().lstrip(".")
    content_type = file.content_type or "application/octet-stream"

    # Create document record
    doc = Document(
        filename=file.filename or "unknown",
        file_type=ext,
        status="processing",
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)

    try:
        # OCR
        ocr_text = await ocr_service.extract_text(file_bytes, file.filename or "", content_type)
        doc.ocr_text = ocr_text

        # Classify (sync call in thread pool)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, classifier_service.classify_document, ocr_text
        )

        doc.doc_type = result["doc_type"]
        doc.confidence = result["confidence"]
        doc.metadata_ = result["metadata"]
        doc.status = "done"

    except Exception as e:
        doc.status = "failed"
        doc.error_msg = str(e)
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Classification failed: {e}") from e

    await db.commit()
    await db.refresh(doc)

    return ClassifyResponse(
        id=doc.id,
        filename=doc.filename,
        doc_type=doc.doc_type,
        doc_type_label=DOC_TYPE_LABELS.get(doc.doc_type, doc.doc_type),
        confidence=doc.confidence or 0.0,
        ocr_text=doc.ocr_text,
        metadata=doc.metadata_ or {},
        created_at=doc.created_at,
    )
