"""
Batch processing service.
Processes documents asynchronously using FastAPI BackgroundTasks.
Updates BatchJob status and Document records in DB.
"""
import asyncio

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.db_models import Document, BatchJob
from app.services import ocr_service, classifier_service


async def process_document(doc_id: str) -> None:
    """Process a single document: OCR → classify → update DB."""
    async with AsyncSessionLocal() as db:
        # Load document
        result = await db.execute(select(Document).where(Document.id == doc_id))
        doc = result.scalar_one_or_none()
        if not doc:
            return

        try:
            # Mark as processing
            doc.status = "processing"
            await db.flush()

            # We need the raw bytes — stored temporarily in a cache attribute
            # (set by the router before enqueueing)
            file_bytes = getattr(doc, "_file_bytes", None)
            content_type = getattr(doc, "_content_type", "application/octet-stream")

            if file_bytes is None:
                raise RuntimeError("File bytes not available for processing")

            # OCR
            ocr_text = await ocr_service.extract_text(file_bytes, doc.filename, content_type)
            doc.ocr_text = ocr_text

            # Classify (sync, run in thread pool)
            loop = asyncio.get_event_loop()
            classification = await loop.run_in_executor(
                None, classifier_service.classify_document, ocr_text
            )

            doc.doc_type = classification["doc_type"]
            doc.confidence = classification["confidence"]
            doc.metadata_ = classification["metadata"]
            doc.status = "done"

        except Exception as e:
            doc.status = "failed"
            doc.error_msg = str(e)

        finally:
            await db.flush()
            # Update batch job counters if applicable
            if doc.batch_job_id:
                await _update_batch_job(db, doc.batch_job_id)
            await db.commit()


async def _update_batch_job(db: AsyncSession, job_id: str) -> None:
    """Recalculate and update batch job status from document statuses."""
    from sqlalchemy import func

    # Count processed (done + failed) and failed documents
    result = await db.execute(
        select(Document.status, func.count(Document.id))
        .where(Document.batch_job_id == job_id)
        .group_by(Document.status)
    )
    counts = {row[0]: row[1] for row in result.all()}

    total_result = await db.execute(
        select(func.count(Document.id)).where(Document.batch_job_id == job_id)
    )
    total = total_result.scalar() or 0

    done = counts.get("done", 0)
    failed = counts.get("failed", 0)
    processed = done + failed

    # Determine overall job status
    if processed >= total and total > 0:
        job_status = "done"
    elif processed > 0:
        job_status = "processing"
    else:
        job_status = "pending"

    await db.execute(
        update(BatchJob)
        .where(BatchJob.id == job_id)
        .values(
            status=job_status,
            processed=processed,
            failed=failed,
        )
    )


async def process_batch_documents(doc_ids_with_bytes: list[tuple[str, bytes, str]]) -> None:
    """
    Background task: process all documents in a batch sequentially.
    doc_ids_with_bytes: list of (doc_id, file_bytes, content_type)
    """
    async with AsyncSessionLocal() as db:
        # Mark batch job as processing when first doc starts
        pass

    for doc_id, file_bytes, content_type in doc_ids_with_bytes:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Document).where(Document.id == doc_id))
            doc = result.scalar_one_or_none()
            if not doc:
                continue

            try:
                doc.status = "processing"
                await db.flush()

                ocr_text = await ocr_service.extract_text(file_bytes, doc.filename, content_type)
                doc.ocr_text = ocr_text

                loop = asyncio.get_event_loop()
                classification = await loop.run_in_executor(
                    None, classifier_service.classify_document, ocr_text
                )

                doc.doc_type = classification["doc_type"]
                doc.confidence = classification["confidence"]
                doc.metadata_ = classification["metadata"]
                doc.status = "done"

            except Exception as e:
                doc.status = "failed"
                doc.error_msg = str(e)

            finally:
                await db.flush()
                if doc.batch_job_id:
                    await _update_batch_job(db, doc.batch_job_id)
                await db.commit()
