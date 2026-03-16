# API Specification — VietDoc Classifier

Base URL: `/api/v1`

---

## POST /api/v1/classify

Phân loại một file chứng từ.

**Request**: `multipart/form-data`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file  | file | yes | JPG/PNG/PDF, max 10MB |

**Response 200**
```json
{
  "id": "uuid",
  "filename": "invoice_001.pdf",
  "doc_type": "hoa_don_vat_dau_vao",
  "confidence": 0.97,
  "ocr_text": "...",
  "metadata": {
    "invoice_number": "0001234",
    "date": "2024-01-15",
    "seller_name": "Công ty ABC",
    "seller_tax_id": "0123456789",
    "buyer_name": "Công ty XYZ",
    "total_amount": 11000000,
    "vat_amount": 1000000
  },
  "created_at": "2024-01-15T10:00:00"
}
```

**Errors**
- `400` — file type không hỗ trợ hoặc file rỗng
- `422` — validation error
- `500` — OCR hoặc LLM lỗi

---

## POST /api/v1/batch

Upload nhiều file, tạo batch job xử lý bất đồng bộ.

**Request**: `multipart/form-data`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| files | file[] | yes | Tối đa 50 files |

**Response 202**
```json
{
  "job_id": "uuid",
  "status": "pending",
  "total": 10,
  "processed": 0,
  "failed": 0,
  "created_at": "2024-01-15T10:00:00"
}
```

---

## GET /api/v1/batch/{job_id}

Lấy trạng thái và kết quả của batch job.

**Response 200**
```json
{
  "job_id": "uuid",
  "status": "done",
  "total": 10,
  "processed": 9,
  "failed": 1,
  "results": [
    {
      "id": "uuid",
      "filename": "file1.pdf",
      "doc_type": "phieu_chi",
      "confidence": 0.94,
      "metadata": {},
      "status": "done",
      "error_msg": null
    }
  ],
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:01:30"
}
```

---

## GET /api/v1/evaluate

Tính accuracy và F1-score từ các document đã được gán nhãn trong DB.

**Query params**
| Param | Default | Description |
|-------|---------|-------------|
| limit | 100 | Số document tối đa |

**Response 200**
```json
{
  "total_evaluated": 100,
  "accuracy": 0.93,
  "per_class_f1": {
    "hoa_don_vat_dau_vao": 0.95,
    "phieu_chi": 0.91,
    "sao_ke_ngan_hang": 0.88
  },
  "macro_f1": 0.90,
  "confusion_counts": {
    "hoa_don_vat_dau_vao": {"correct": 19, "total": 20}
  }
}
```

---

## GET /health

```json
{"status": "ok", "service": "vietdoc-classifier"}
```
