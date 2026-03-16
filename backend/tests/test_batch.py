"""Tests for POST /api/v1/batch and GET /api/v1/batch/{job_id}."""
from unittest.mock import patch, AsyncMock

import pytest
from httpx import AsyncClient


MOCK_OCR_TEXT = "Phiếu chi số 001 ngày 15/01/2024"
MOCK_CLASSIFICATION = {
    "doc_type": "phieu_chi",
    "confidence": 0.92,
    "metadata": {"voucher_number": "001", "date": "2024-01-15", "amount": 5000000},
}


@patch("app.routers.batch.process_batch_documents", new_callable=AsyncMock)
async def test_batch_create_success(mock_process, client: AsyncClient):
    files = [
        ("files", ("doc1.pdf", b"%PDF-1.4 test1", "application/pdf")),
        ("files", ("doc2.pdf", b"%PDF-1.4 test2", "application/pdf")),
    ]
    response = await client.post("/api/v1/batch", files=files)
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["total"] == 2
    assert data["status"] == "pending"
    assert mock_process.called


@patch("app.routers.batch.process_batch_documents", new_callable=AsyncMock)
async def test_batch_get_status(mock_process, client: AsyncClient):
    # Create a batch
    files = [
        ("files", ("file1.pdf", b"%PDF-1.4 content", "application/pdf")),
    ]
    create_res = await client.post("/api/v1/batch", files=files)
    assert create_res.status_code == 202
    job_id = create_res.json()["job_id"]

    # Get status
    status_res = await client.get(f"/api/v1/batch/{job_id}")
    assert status_res.status_code == 200
    data = status_res.json()
    assert data["job_id"] == job_id
    assert data["total"] == 1
    assert "results" in data
    assert len(data["results"]) == 1


async def test_batch_not_found(client: AsyncClient):
    response = await client.get("/api/v1/batch/nonexistent-id")
    assert response.status_code == 404


async def test_batch_no_files(client: AsyncClient):
    response = await client.post("/api/v1/batch", files=[])
    assert response.status_code in (400, 422)


async def test_batch_unsupported_file(client: AsyncClient):
    files = [("files", ("doc.docx", b"word", "application/msword"))]
    response = await client.post("/api/v1/batch", files=files)
    assert response.status_code == 400
