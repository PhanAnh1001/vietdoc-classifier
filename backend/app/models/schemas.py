from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


# ── Auth schemas ──────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: str
    password: str


# ── Document / Classify schemas ───────────────────────────────────────────

DOC_TYPES = [
    "hoa_don_vat_dau_vao",
    "hoa_don_vat_dau_ra",
    "phieu_chi",
    "phieu_thu",
    "sao_ke_ngan_hang",
    "giay_uy_quyen",
    "thong_bao_cong_no",
    "thong_bao_ghi_co",
    "bien_lai",
    "hop_dong",
    "phieu_ke_toan",
    "bang_luong",
    "khac",
]

DOC_TYPE_LABELS = {
    "hoa_don_vat_dau_vao": "Hóa đơn VAT đầu vào",
    "hoa_don_vat_dau_ra": "Hóa đơn VAT đầu ra",
    "phieu_chi": "Phiếu chi",
    "phieu_thu": "Phiếu thu",
    "sao_ke_ngan_hang": "Sao kê ngân hàng",
    "giay_uy_quyen": "Giấy ủy quyền",
    "thong_bao_cong_no": "Thông báo công nợ",
    "thong_bao_ghi_co": "Thông báo ghi có",
    "bien_lai": "Biên lai",
    "hop_dong": "Hợp đồng",
    "phieu_ke_toan": "Phiếu kế toán",
    "bang_luong": "Bảng lương",
    "khac": "Khác",
}


class ClassifyResponse(BaseModel):
    id: str
    filename: str
    doc_type: str
    doc_type_label: str
    confidence: float
    ocr_text: Optional[str] = None
    metadata: dict[str, Any] = {}
    created_at: datetime


class BatchJobResponse(BaseModel):
    job_id: str
    status: str
    total: int
    processed: int
    failed: int
    created_at: datetime


class BatchDocumentResult(BaseModel):
    id: str
    filename: str
    doc_type: Optional[str] = None
    doc_type_label: Optional[str] = None
    confidence: Optional[float] = None
    metadata: dict[str, Any] = {}
    status: str
    error_msg: Optional[str] = None


class BatchJobDetailResponse(BaseModel):
    job_id: str
    status: str
    total: int
    processed: int
    failed: int
    results: list[BatchDocumentResult] = []
    created_at: datetime
    updated_at: datetime


class EvaluateResponse(BaseModel):
    total_evaluated: int
    accuracy: float
    per_class_f1: dict[str, float]
    macro_f1: float
    confusion_counts: dict[str, dict[str, int]]
