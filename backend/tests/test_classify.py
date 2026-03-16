"""Tests for POST /api/v1/classify endpoint."""
import io
from unittest.mock import patch, AsyncMock

import pytest
from httpx import AsyncClient


MOCK_OCR_TEXT = "CÔNG TY TNHH ABC\nHÓA ĐƠN GIÁ TRỊ GIA TĂNG\nSố: 0001234\nNgày 15/01/2024"
MOCK_CLASSIFICATION = {
    "doc_type": "hoa_don_vat_dau_vao",
    "confidence": 0.97,
    "metadata": {
        "invoice_number": "0001234",
        "date": "2024-01-15",
        "seller_name": "CÔNG TY TNHH ABC",
        "total_amount": 11000000,
    },
}


@pytest.fixture
def pdf_file():
    """Minimal valid-ish PDF bytes for upload testing."""
    return io.BytesIO(b"%PDF-1.4 minimal pdf content for testing")


@pytest.fixture
def png_file():
    """Minimal PNG bytes (1x1 pixel)."""
    import base64
    # 1x1 white PNG
    png_b64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8"
        "/5+hHgAHggJ/PchI6QAAAABJRU5ErkJggg=="
    )
    return io.BytesIO(base64.b64decode(png_b64))


@patch("app.services.classifier_service.classify_document", return_value=MOCK_CLASSIFICATION)
@patch("app.services.ocr_service.extract_text", new_callable=AsyncMock, return_value=MOCK_OCR_TEXT)
async def test_classify_pdf_success(mock_ocr, mock_classify, client: AsyncClient):
    response = await client.post(
        "/api/v1/classify",
        files={"file": ("invoice.pdf", b"%PDF-1.4 test content", "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["doc_type"] == "hoa_don_vat_dau_vao"
    assert data["confidence"] == 0.97
    assert data["filename"] == "invoice.pdf"
    assert "invoice_number" in data["metadata"]
    assert data["doc_type_label"] == "Hóa đơn VAT đầu vào"


@patch("app.services.classifier_service.classify_document", return_value=MOCK_CLASSIFICATION)
@patch("app.services.ocr_service.extract_text", new_callable=AsyncMock, return_value=MOCK_OCR_TEXT)
async def test_classify_png_success(mock_ocr, mock_classify, client: AsyncClient):
    response = await client.post(
        "/api/v1/classify",
        files={"file": ("doc.png", b"\x89PNG\r\n\x1a\n test", "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["doc_type"] == "hoa_don_vat_dau_vao"


async def test_classify_unsupported_type(client: AsyncClient):
    response = await client.post(
        "/api/v1/classify",
        files={"file": ("doc.docx", b"word content", "application/msword")},
    )
    assert response.status_code == 400
    assert "not supported" in response.json()["detail"]


async def test_classify_empty_file(client: AsyncClient):
    response = await client.post(
        "/api/v1/classify",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


@patch("app.services.ocr_service.extract_text", new_callable=AsyncMock, side_effect=RuntimeError("OCR failed"))
async def test_classify_ocr_failure(mock_ocr, client: AsyncClient):
    response = await client.post(
        "/api/v1/classify",
        files={"file": ("invoice.pdf", b"%PDF-1.4 test", "application/pdf")},
    )
    assert response.status_code == 500
    assert "Classification failed" in response.json()["detail"]
