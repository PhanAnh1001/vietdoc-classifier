"""
Classifier service: classify Vietnamese accounting/banking documents.
Uses Groq Llama 3.3 70B with a structured JSON prompt.
"""
import json
import re

from app.config import settings
from app.models.schemas import DOC_TYPES


CLASSIFICATION_PROMPT = """\
Bạn là chuyên gia phân loại chứng từ kế toán, ngân hàng tiếng Việt.
Phân loại văn bản sau vào đúng 1 trong 13 loại:

- hoa_don_vat_dau_vao: Hóa đơn VAT đầu vào (mua hàng/nhập hàng)
- hoa_don_vat_dau_ra: Hóa đơn VAT đầu ra (bán hàng/xuất hàng)
- phieu_chi: Phiếu chi (xuất quỹ tiền mặt)
- phieu_thu: Phiếu thu (thu tiền mặt vào quỹ)
- sao_ke_ngan_hang: Sao kê ngân hàng (bank statement)
- giay_uy_quyen: Giấy ủy quyền
- thong_bao_cong_no: Thông báo công nợ / đối chiếu công nợ
- thong_bao_ghi_co: Thông báo ghi có / xác nhận chuyển khoản
- bien_lai: Biên lai thu tiền / biên lai thanh toán
- hop_dong: Hợp đồng kinh tế / hợp đồng dịch vụ
- phieu_ke_toan: Phiếu kế toán / bút toán ghi sổ
- bang_luong: Bảng lương / bảng thanh toán lương
- khac: Loại khác không thuộc các loại trên

Yêu cầu trả về JSON hợp lệ (không có markdown fence), gồm:
- doc_type: tên loại (string, bắt buộc)
- confidence: độ tin cậy từ 0.0 đến 1.0 (float, bắt buộc)
- metadata: object chứa các trường phù hợp với loại tài liệu (object, bắt buộc)

Ví dụ metadata tương ứng:
- hóa đơn: invoice_number, date, seller_name, seller_tax_id, buyer_name, buyer_tax_id, total_before_vat, vat_rate, vat_amount, total_amount
- phiếu chi/thu: voucher_number, date, amount, payer_or_payee, description
- sao kê: account_number, bank_name, period_start, period_end, opening_balance, closing_balance
- hợp đồng: contract_number, date, party_a, party_b, contract_value, effective_date
- bảng lương: period, total_employees, total_gross, total_net

Văn bản tài liệu:
{text}"""


def _parse_llm_json(raw: str) -> dict:
    """Parse JSON from LLM output, stripping markdown fences if present."""
    # Remove markdown code fences
    cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip()
    cleaned = cleaned.rstrip("`").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to extract JSON object with regex
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Cannot parse LLM response as JSON: {raw[:200]}")


def classify_document(ocr_text: str) -> dict:
    """
    Classify document text using Groq LLM.
    Returns dict with doc_type, confidence, metadata.
    """
    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not configured")

    if not ocr_text or not ocr_text.strip():
        return {"doc_type": "khac", "confidence": 0.0, "metadata": {}}

    from groq import Groq  # type: ignore

    client = Groq(api_key=settings.GROQ_API_KEY)

    # Truncate to ~6000 chars to stay within token limits
    text_input = ocr_text[:6000]
    prompt = CLASSIFICATION_PROMPT.format(text=text_input)

    completion = client.chat.completions.create(
        model=settings.GROQ_LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.1,  # Low temperature for deterministic classification
    )

    raw_output = completion.choices[0].message.content or ""
    result = _parse_llm_json(raw_output)

    # Validate and normalize doc_type
    doc_type = result.get("doc_type", "khac")
    if doc_type not in DOC_TYPES:
        doc_type = "khac"

    confidence = float(result.get("confidence", 0.5))
    confidence = max(0.0, min(1.0, confidence))

    metadata = result.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}

    return {"doc_type": doc_type, "confidence": confidence, "metadata": metadata}
