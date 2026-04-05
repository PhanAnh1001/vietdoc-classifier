# VietDoc Classifier

> Hệ thống tự động phân loại chứng từ kế toán, ngân hàng tiếng Việt bằng AI — accuracy ≥ 90% trên 13 loại tài liệu.

**[English](README.md)**

Doanh nghiệp Việt Nam xử lý hàng trăm chứng từ tài chính mỗi ngày. Phân loại thủ công chậm và dễ sai sót khi xử lý số lượng lớn. Hệ thống này tự động hóa quy trình bằng pipeline LLM 2 bước: **Vision OCR → zero-shot classification + trích xuất metadata có cấu trúc**.

---

## Cách hoạt động

1. Upload file PDF, JPG hoặc PNG (hóa đơn, phiếu chi, sao kê ngân hàng, ...)
2. **OCR**: Groq Llama Vision trích xuất text từ ảnh; pypdf xử lý PDF có text sẵn
3. **Phân loại**: Groq Llama 3.3 70B trả về loại chứng từ + confidence score + metadata trích xuất
4. Kết quả hiển thị ngay — số hóa đơn, ngày tháng, mã số thuế, số tiền được lấy tự động

**Batch mode**: upload tối đa 50 file cùng lúc, xử lý bất đồng bộ, theo dõi trạng thái real-time.

---

## AI Pipeline

```
File (PDF / JPG / PNG)
        │
        ▼
  ┌─── Giai đoạn OCR ──────────────────────────┐
  │  PDF  ──► pypdf text extraction            │
  │  Ảnh  ──► Groq Llama 3.2 Vision (11B)     │
  └─────────────────────────────────────────────┘
        │ văn bản thô (~6 000 ký tự)
        ▼
  ┌─── Giai đoạn phân loại ────────────────────┐
  │  Groq Llama 3.3 70B                        │
  │  Zero-shot prompt → JSON có cấu trúc       │
  │  { doc_type, confidence, metadata{} }      │
  └─────────────────────────────────────────────┘
        │
        ▼
  PostgreSQL (lưu Document record) + API response
```

### Prompt Engineering

**Vấn đề**: LLM phải trả về schema JSON khác nhau tuỳ loại tài liệu — hóa đơn cần số hóa đơn, MST, chi tiết VAT; bảng lương cần kỳ lương, số nhân viên, tổng lương; v.v.

**Giải pháp**: một prompt duy nhất với schema hướng dẫn per-type, `temperature=0.1` để đầu ra gần như deterministic, JSON parser chắc chắn có thể xử lý markdown fences và fallback bằng regex.

```python
# classifier_service.py — chiến lược prompt
completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=1024,
    temperature=0.1,   # gần deterministic cho bài toán classification
)
```

### 13 Loại chứng từ được hỗ trợ

| Key | Tên tiếng Việt |
|-----|----------------|
| `hoa_don_vat_dau_vao` | Hóa đơn VAT đầu vào |
| `hoa_don_vat_dau_ra` | Hóa đơn VAT đầu ra |
| `phieu_chi` | Phiếu chi |
| `phieu_thu` | Phiếu thu |
| `sao_ke_ngan_hang` | Sao kê ngân hàng |
| `giay_uy_quyen` | Giấy ủy quyền |
| `thong_bao_cong_no` | Thông báo công nợ |
| `thong_bao_ghi_co` | Thông báo ghi có |
| `bien_lai` | Biên lai |
| `hop_dong` | Hợp đồng |
| `phieu_ke_toan` | Phiếu kế toán |
| `bang_luong` | Bảng lương |
| `khac` | Khác |

---

## Tech Stack

| Layer | Công nghệ | Lý do chọn |
|-------|-----------|-------------|
| LLM | Groq Llama 3.3 70B | Inference nhanh nhất hiện tại, free tier rộng rãi |
| Vision OCR | Groq Llama 3.2 Vision 11B | Multimodal — xử lý ảnh scan và ảnh chụp |
| PDF OCR | pypdf | Trích xuất text tất định, không cần API call |
| Backend | FastAPI (async) | Non-blocking I/O cho upload file + LLM calls đồng thời |
| Frontend | Next.js 15 + TypeScript | App Router, typing chặt chẽ end-to-end |
| Database | PostgreSQL + SQLAlchemy async | Lưu lịch sử + ground truth label cho evaluation |
| Queue | FastAPI BackgroundTasks | Zero infra, đủ dùng cho batch ≤ 50 files |
| Deploy | Vercel + Render + AWS Lightsail | $0 – $3.50/tháng |

---

## Kiến trúc hệ thống

```
┌─────────────┐   REST/multipart   ┌─────────────┐    async    ┌──────────────────────┐
│   Vercel    │ ─────────────────▶ │   Render    │ ──────────▶ │    AWS Lightsail     │
│  Next.js 15 │                    │   FastAPI   │             │  PostgreSQL + Redis  │
└─────────────┘                    └──────┬──────┘             └──────────────────────┘
                                          │ HTTP
                                          ▼
                                   ┌─────────────┐
                                   │ Groq Cloud  │
                                   │ Llama Vision│
                                   │  Llama 3.3  │
                                   └─────────────┘
```

---

## Chạy nhanh (Local)

**Yêu cầu**: Docker, Docker Compose, [Groq API key](https://console.groq.com) (miễn phí)

```bash
git clone https://github.com/PhanAnh1001/vietdoc-classifier
cd vietdoc-classifier

# Cấu hình môi trường
cp .env.example .env
# Điền GROQ_API_KEY vào file .env

# Khởi động tất cả services (PostgreSQL + Redis + Backend + Frontend)
docker compose up -d

# Chạy DB migration
docker compose exec backend psql $DATABASE_URL -f migrations/init.sql
docker compose exec backend psql $DATABASE_URL -f migrations/v2_documents.sql
```

- Frontend: http://localhost:3000
- API docs (Swagger UI): http://localhost:8000/docs

---

## API

```
POST /api/v1/classify          Upload 1 file → doc_type + confidence + metadata
POST /api/v1/batch             Upload ≤ 50 files → job_id (async)
GET  /api/v1/batch/{job_id}    Lấy trạng thái batch + kết quả từng file
GET  /api/v1/evaluate          Accuracy + per-class F1 từ labeled documents
GET  /health
```

Chi tiết: [`docs/technical/api-spec.md`](docs/technical/api-spec.md)

---

## Phát triển

### Backend (FastAPI)
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload   # http://localhost:8000

# Chạy tests (19 tests, SQLite in-memory, không cần Groq key)
uv run pytest tests/ -v
```

### Frontend (Next.js)
```bash
cd app
npm install
npm run dev        # http://localhost:3000
npm test           # Vitest unit tests
npm run test:e2e   # Playwright E2E tests
```

---

## Cấu trúc project

```
├── app/                              # Next.js 15 frontend
│   └── src/
│       ├── app/(dashboard)/
│       │   ├── classify/             # Upload file đơn lẻ + hiển thị kết quả
│       │   ├── batch/                # Upload batch + polling real-time
│       │   └── evaluate/             # Dashboard accuracy / F1
│       ├── components/classify/      # Component ClassifyResult
│       └── lib/api.ts                # API client có typing đầy đủ
│
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── ocr_service.py        # PDF pypdf + Groq Vision OCR
│   │   │   ├── classifier_service.py # Groq LLM prompt + JSON parsing
│   │   │   └── batch_service.py      # Async batch processor
│   │   └── routers/
│   │       ├── classify.py           # POST /classify
│   │       ├── batch.py              # POST /batch, GET /batch/{id}
│   │       └── evaluate.py           # GET /evaluate
│   ├── migrations/
│   │   ├── init.sql                  # Bảng users
│   │   └── v2_documents.sql          # Bảng documents + batch_jobs
│   └── tests/                        # 19 pytest tests (mock LLM)
│
└── docs/technical/
    ├── api-spec.md
    ├── db-schema.md
    └── classifier-design.md          # Chiến lược prompt + metadata schemas
```

---

## Đánh giá mô hình

`GET /api/v1/evaluate` tính toán từ các document đã được gán nhãn (`ground_truth`):

- **Accuracy tổng** — số dự đoán đúng / tổng số mẫu
- **Per-class F1** — trung bình điều hòa của precision và recall cho từng loại chứng từ
- **Macro F1** — trung bình F1 không trọng số trên tất cả các class

**Mục tiêu**: accuracy ≥ 90%, per-class F1 ≥ 0.85 cho 6 loại phổ biến nhất.

---

## Quyết định thiết kế

**Tại sao zero-shot thay vì fine-tuned model?**
Llama 3.3 70B đạt accuracy đủ cao mà không cần dữ liệu huấn luyện được gán nhãn, không tốn chi phí fine-tuning, và thêm loại chứng từ mới chỉ cần sửa prompt — không cần huấn luyện lại.

**Tại sao BackgroundTasks thay vì Celery + Redis queue?**
Batch size giới hạn ở 50 files, không cần distributed workers. BackgroundTasks đơn giản hơn, zero infra. Có thể nâng lên Celery sau bằng cách swap một service duy nhất.

**Tại sao Groq thay vì OpenAI?**
Inference nhanh hơn ~10x trên cùng kích cỡ model, free tier 14.400 tokens/phút đủ cho MVP, không cần thẻ tín dụng để bắt đầu.

---

## Triển khai

### Backend → Render (Docker)
```bash
# render.yaml đã được cấu hình sẵn
# Set các env vars sau trên Render dashboard:
# DATABASE_URL, REDIS_URL, GROQ_API_KEY
```

### Frontend → Vercel
```bash
# Auto-deploy từ nhánh master
# Set: NEXT_PUBLIC_API_URL=https://your-service.onrender.com
```

### Database + Redis → AWS Lightsail ($3.50/tháng)
```bash
ssh user@<lightsail-ip>
docker compose -f docker-compose.prod.yml up -d
psql $DATABASE_URL -f migrations/init.sql
psql $DATABASE_URL -f migrations/v2_documents.sql
```

---

## Giấy phép

MIT
