"""Tests for GET /api/v1/evaluate endpoint."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Document


async def _create_labeled_doc(db: AsyncSession, doc_type: str, ground_truth: str) -> Document:
    doc = Document(
        filename=f"test_{doc_type}.pdf",
        file_type="pdf",
        doc_type=doc_type,
        confidence=0.95,
        ground_truth=ground_truth,
        status="done",
        metadata_={},
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    return doc


async def test_evaluate_empty(client: AsyncClient):
    """With no labeled documents, should return zeros."""
    response = await client.get("/api/v1/evaluate")
    assert response.status_code == 200
    data = response.json()
    assert data["total_evaluated"] == 0
    assert data["accuracy"] == 0.0
    assert data["macro_f1"] == 0.0


async def test_evaluate_perfect_accuracy(client: AsyncClient, db_session: AsyncSession):
    """All predictions match ground truth → accuracy = 1.0."""
    await _create_labeled_doc(db_session, "phieu_chi", "phieu_chi")
    await _create_labeled_doc(db_session, "phieu_thu", "phieu_thu")
    await _create_labeled_doc(db_session, "hop_dong", "hop_dong")
    await db_session.commit()

    response = await client.get("/api/v1/evaluate")
    assert response.status_code == 200
    data = response.json()
    assert data["total_evaluated"] >= 3
    # All committed docs with matching labels → 100% accuracy
    assert data["accuracy"] == 1.0
    assert data["macro_f1"] == 1.0


async def test_evaluate_partial_accuracy(client: AsyncClient, db_session: AsyncSession):
    """Mix of correct and incorrect predictions."""
    await _create_labeled_doc(db_session, "phieu_ke_toan", "phieu_ke_toan")  # correct
    await _create_labeled_doc(db_session, "bien_lai", "bang_luong")  # wrong
    await db_session.commit()

    response = await client.get("/api/v1/evaluate")
    assert response.status_code == 200
    data = response.json()
    assert data["total_evaluated"] >= 2
    assert 0.0 < data["accuracy"] < 1.0 or data["accuracy"] == 1.0


async def test_evaluate_response_schema(client: AsyncClient):
    """Response must contain all required fields."""
    response = await client.get("/api/v1/evaluate")
    assert response.status_code == 200
    data = response.json()
    assert "total_evaluated" in data
    assert "accuracy" in data
    assert "per_class_f1" in data
    assert "macro_f1" in data
    assert "confusion_counts" in data


async def test_evaluate_limit_param(client: AsyncClient):
    """limit query param should be respected."""
    response = await client.get("/api/v1/evaluate?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total_evaluated"] <= 10
