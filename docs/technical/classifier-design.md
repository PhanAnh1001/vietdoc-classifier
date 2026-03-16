# Classifier Design — VietDoc Classifier

## Pipeline

```
File Upload (JPG/PNG/PDF)
        │
        ▼
    OCR Stage
  ┌─────────────────────────────────────────┐
  │ PDF  → pypdf text extraction            │
  │ Image → Groq Llama Vision (llama-3.2-11b-vision-preview) │
  └─────────────────────────────────────────┘
        │ raw OCR text
        ▼
  Classification Stage
  ┌───────────────────────────────────────┐
  │ Groq Llama 3.3 70B                   │
  │ Zero-shot + schema-guided JSON output │
  └───────────────────────────────────────┘
        │ {doc_type, confidence, metadata}
        ▼
    Store in DB + return response
```

---

## Stage 1: Classification Prompt

```
Bạn là chuyên gia phân loại chứng từ kế toán, ngân hàng tiếng Việt.
Phân loại văn bản sau vào đúng 1 trong 13 loại:

- hoa_don_vat_dau_vao: Hóa đơn VAT đầu vào (mua hàng)
- hoa_don_vat_dau_ra: Hóa đơn VAT đầu ra (bán hàng)
- phieu_chi: Phiếu chi (xuất quỹ tiền mặt)
- phieu_thu: Phiếu thu (thu tiền mặt)
- sao_ke_ngan_hang: Sao kê ngân hàng
- giay_uy_quyen: Giấy ủy quyền
- thong_bao_cong_no: Thông báo công nợ / đối chiếu công nợ
- thong_bao_ghi_co: Thông báo ghi có / chuyển khoản
- bien_lai: Biên lai thu tiền
- hop_dong: Hợp đồng kinh tế
- phieu_ke_toan: Phiếu kế toán / bút toán
- bang_luong: Bảng lương
- khac: Loại khác

Trả về JSON (không có markdown):
{
  "doc_type": "<loại>",
  "confidence": <0.0-1.0>,
  "metadata": { <các trường phù hợp> }
}

Văn bản:
{text}
```

---

## Stage 2: Metadata Schemas per Doc Type

### hoa_don_vat_dau_vao / hoa_don_vat_dau_ra
```json
{
  "invoice_number": "string",
  "date": "YYYY-MM-DD",
  "seller_name": "string",
  "seller_tax_id": "string",
  "buyer_name": "string",
  "buyer_tax_id": "string",
  "total_before_vat": number,
  "vat_rate": number,
  "vat_amount": number,
  "total_amount": number,
  "currency": "VND"
}
```

### phieu_chi / phieu_thu
```json
{
  "voucher_number": "string",
  "date": "YYYY-MM-DD",
  "amount": number,
  "currency": "VND",
  "payer_or_payee": "string",
  "description": "string",
  "approver": "string"
}
```

### sao_ke_ngan_hang
```json
{
  "account_number": "string",
  "bank_name": "string",
  "period_start": "YYYY-MM-DD",
  "period_end": "YYYY-MM-DD",
  "opening_balance": number,
  "closing_balance": number,
  "currency": "VND"
}
```

### hop_dong
```json
{
  "contract_number": "string",
  "date": "YYYY-MM-DD",
  "party_a": "string",
  "party_b": "string",
  "contract_value": number,
  "currency": "VND",
  "effective_date": "YYYY-MM-DD",
  "expiry_date": "YYYY-MM-DD"
}
```

### bang_luong
```json
{
  "period": "YYYY-MM",
  "company_name": "string",
  "total_employees": number,
  "total_gross": number,
  "total_net": number,
  "currency": "VND"
}
```

---

## Evaluation Targets
- Overall accuracy ≥ 90% on 100 test samples
- Per-class F1 ≥ 0.85 for top 6 types
- Ground truth stored in `documents.ground_truth` column
