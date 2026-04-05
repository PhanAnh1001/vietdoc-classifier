"""
OCR service: extract text from uploaded files.
- PDF: pypdf direct text extraction
- Images (JPG/PNG): Groq Llama Vision
"""
import base64
import io
from pathlib import Path

from app.config import settings


SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png"}
SUPPORTED_TYPES = SUPPORTED_IMAGE_TYPES | {"application/pdf"}


def _extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from PDF using pypdf."""
    try:
        import pypdf  # type: ignore

        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text.strip())
        return "\n\n".join(t for t in pages_text if t)
    except Exception as e:
        raise RuntimeError(f"PDF text extraction failed: {e}") from e


def _extract_image_text_groq(file_bytes: bytes, content_type: str) -> str:
    """Extract text from image via Groq Llama Vision API."""
    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not configured")

    from groq import Groq  # type: ignore

    client = Groq(api_key=settings.GROQ_API_KEY)

    # Determine media type
    media_type = "image/jpeg" if "jpeg" in content_type or "jpg" in content_type else "image/png"
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    data_url = f"data:{media_type};base64,{b64}"

    completion = client.chat.completions.create(
        model=settings.GROQ_VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url},
                    },
                    {
                        "type": "text",
                        "text": (
                            "Đây là chứng từ kế toán hoặc tài liệu ngân hàng tiếng Việt. "
                            "Hãy trích xuất toàn bộ nội dung văn bản trong ảnh, "
                            "bao gồm tất cả số liệu, ngày tháng, tên, mã số. "
                            "Chỉ trả về văn bản thuần túy, không giải thích."
                        ),
                    },
                ],
            }
        ],
        max_tokens=2048,
    )
    return completion.choices[0].message.content or ""


async def extract_text(file_bytes: bytes, filename: str, content_type: str) -> str:
    """Extract text from a file. Returns OCR text."""
    ext = Path(filename).suffix.lower()

    if content_type == "application/pdf" or ext == ".pdf":
        return _extract_pdf_text(file_bytes)
    elif content_type in SUPPORTED_IMAGE_TYPES or ext in {".jpg", ".jpeg", ".png"}:
        return _extract_image_text_groq(file_bytes, content_type)
    else:
        raise ValueError(f"Unsupported file type: {content_type} ({ext})")
