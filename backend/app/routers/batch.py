"""
POST /api/v1/batch — batch file classification
GET  /api/v1/batch/{job_id} — batch job status
"""
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.db_models import Document, BatchJob
from app.models.schemas import (
    BatchJobResponse,
    BatchJobDetailResponse,
    BatchDocumentResult,
    DOC_TYPE_LABELS,
)
from app.services.batch_service import process_batch_documents

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}


def _validate_files(files: list[UploadFile]) -> None:
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    if len(files) > settings.MAX_BATCH_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Max: {settings.MAX_BATCH_FILES}",
        )
    for f in files:
        ext = Path(f.filename or "").suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File '{f.filename}' has unsupported type. Use JPG, PNG, or PDF.",
            )


@router.post("", response_model=BatchJobResponse, status_code=202)
async def create_batch(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    _validate_files(files)

    # Create batch job
    job = BatchJob(status="pending", total=len(files))
    db.add(job)
    await db.flush()
    await db.refresh(job)

    # Read all file bytes and create document records
    docs_data: list[tuple[str, bytes, str]] = []
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024

    for upload in files:
        file_bytes = await upload.read()
        if len(file_bytes) > max_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File '{upload.filename}' too large. Max: {settings.MAX_FILE_SIZE_MB}MB",
            )

        ext = Path(upload.filename or "file").suffix.lower().lstrip(".")
        content_type = upload.content_type or "application/octet-stream"

        doc = Document(
            filename=upload.filename or "unknown",
            file_type=ext,
            batch_job_id=job.id,
            status="pending",
        )
        db.add(doc)
        await db.flush()
        await db.refresh(doc)

        docs_data.append((doc.id, file_bytes, content_type))

    await db.commit()
    await db.refresh(job)

    # Enqueue background processing
    background_tasks.add_task(process_batch_documents, docs_data)

    return BatchJobResponse(
        job_id=job.id,
        status=job.status,
        total=job.total,
        processed=job.processed,
        failed=job.failed,
        created_at=job.created_at,
    )


@router.get("/{job_id}", response_model=BatchJobDetailResponse)
async def get_batch_status(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BatchJob).where(BatchJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Batch job not found")

    docs_result = await db.execute(
        select(Document).where(Document.batch_job_id == job_id).order_by(Document.created_at)
    )
    docs = docs_result.scalars().all()

    results = [
        BatchDocumentResult(
            id=d.id,
            filename=d.filename,
            doc_type=d.doc_type,
            doc_type_label=DOC_TYPE_LABELS.get(d.doc_type, d.doc_type) if d.doc_type else None,
            confidence=d.confidence,
            metadata=d.metadata_ or {},
            status=d.status,
            error_msg=d.error_msg,
        )
        for d in docs
    ]

    return BatchJobDetailResponse(
        job_id=job.id,
        status=job.status,
        total=job.total,
        processed=job.processed,
        failed=job.failed,
        results=results,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
