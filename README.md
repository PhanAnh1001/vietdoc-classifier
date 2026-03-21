# VietDoc Classifier

> Hệ thống phân loại tự động chứng từ kế toán, ngân hàng tiếng Việt bằng AI — accuracy ≥ 90% trên 13 loại tài liệu.

Vietnamese enterprises process hundreds of financial documents daily. Manual classification is slow and error-prone at scale. This system automates the workflow using a two-stage LLM pipeline: **Vision OCR → zero-shot classification + structured metadata extraction**.

---

## Demo

| Bước | Mô tả |
|------|--------|
| 1 | Upload file PDF/JPG/PNG (hóa đơn, phiếu chi, sao kê, ...) |
| 2 | OCR: Groq Llama Vision trích xuất text; PDF dùng pypdf |
| 3 | Classify: Groq Llama 3.3 70B trả về loại + confidence + metadata |
| 4 | Kết quả hiển thị ngay, metadata trích xuất tự động (số HĐ, ngày, MST, số tiền...) |

**Batch mode**: upload 50 file cùng lúc, xử lý bất đồng bộ, polling trạng thái real-time.

---

## AI Pipeline

```
File (PDF / JPG / PNG)
        │
        ▼
  ┌─── OCR Stage ──────────────────────────────┐
  │  PDF  ──► pypdf text extraction            │
  │  Image ──► Groq Llama 3.2 Vision (11B)    │
  └─────────────────────────────────────────────┘
        │ raw text (~6 000 chars)
        ▼
  ┌─── Classification Stage ───────────────────┐
  │  Groq Llama 3.3 70B                        │
  │  Zero-shot prompt → structured JSON output │
  │  { doc_type, confidence, metadata{} }      │
  └─────────────────────────────────────────────┘
        │
        ▼
  PostgreSQL (Document record) + API response
```

### Prompt Engineering

**Vấn đề**: LLM cần trả về JSON có cấu trúc khác nhau tuỳ loại tài liệu (hóa đơn → số hóa đơn, MST; bảng lương → period, tổng lương...).

**Giải pháp**: một prompt duy nhất với schema hướng dẫn per-type, kết hợp `temperature=0.1` để đầu ra deterministic; robust JSON parser xử lý markdown fences và regex fallback.

```python
# classifier_service.py — core prompt strategy
completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=1024,
    temperature=0.1,   # near-deterministic for classification tasks
)
```

### 13 Supported Document Types

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

| Layer | Technology | Lý do chọn |
|-------|-----------|-------------|
| LLM | Groq Llama 3.3 70B | Fastest inference, free tier đủ dùng |
| Vision OCR | Groq Llama 3.2 Vision 11B | Multimodal, xử lý scan/ảnh chụp |
| PDF OCR | pypdf | Deterministic, không cần API cho PDF text |
| Backend | FastAPI (async) | Async I/O cho file upload + LLM calls |
| Frontend | Next.js 15 + TypeScript | App Router, SSR |
| Database | PostgreSQL + SQLAlchemy async | Lưu lịch sử + ground truth cho evaluation |
| Queue | FastAPI BackgroundTasks | Đơn giản, đủ cho batch ≤ 50 files |
| Deploy | Vercel + Render + AWS Lightsail | $0 → $3.50/month |

---

## System Architecture

```
┌─────────────┐     REST/multipart     ┌─────────────┐     async     ┌──────────────────┐
│   Vercel    │ ──────────────────────▶│   Render    │ ────────────▶│  AWS Lightsail   │
│  Next.js 15 │                        │   FastAPI   │              │  PostgreSQL + Redis│
└─────────────┘                        └──────┬──────┘              └──────────────────┘
                                              │ HTTP
                                              ▼
                                       ┌─────────────┐
                                       │  Groq Cloud  │
                                       │  Llama Vision│
                                       │  Llama 3.3  │
                                       └─────────────┘
```

---

## Quick Start

**Yêu cầu**: Docker, Docker Compose, [Groq API key](https://console.groq.com) (free)

```bash
git clone https://github.com/PhanAnh1001/vietdoc-classifier
cd vietdoc-classifier

# Setup env
cp .env.example .env
# Điền GROQ_API_KEY vào .env

# Start tất cả services (PostgreSQL + Redis + Backend + Frontend)
docker compose up -d

# Chạy DB migration
docker compose exec backend psql $DATABASE_URL -f migrations/v2_documents.sql
```

- Frontend: http://localhost:3000
- API docs (Swagger): http://localhost:8000/docs

---

## API

```
POST /api/v1/classify          Upload 1 file → doc_type + confidence + metadata
POST /api/v1/batch             Upload ≤ 50 files → job_id (async)
GET  /api/v1/batch/{job_id}    Poll batch status + kết quả từng file
GET  /api/v1/evaluate          Accuracy + per-class F1 từ labeled documents
GET  /health
```

Chi tiết: [`docs/technical/api-spec.md`](docs/technical/api-spec.md)

---

## Development

### Backend (FastAPI)
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload   # :8000

# Tests (16 tests, SQLite in-memory, không cần Groq key)
uv run pytest tests/ -v
```

### Frontend (Next.js)
```bash
cd app
npm install
npm run dev        # :3000
npm test           # Vitest
npm run test:e2e   # Playwright
```

---

## Project Structure

```
├── app/                          # Next.js 15 frontend
│   └── src/
│       ├── app/(dashboard)/
│       │   ├── classify/         # Single file upload + result
│       │   ├── batch/            # Batch upload + polling
│       │   └── evaluate/         # Accuracy / F1 dashboard
│       ├── components/classify/  # ClassifyResult card
│       └── lib/api.ts            # Typed API client
│
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── ocr_service.py        # PDF / Vision OCR
│   │   │   ├── classifier_service.py # Groq LLM + prompt
│   │   │   └── batch_service.py      # Async batch processor
│   │   └── routers/
│   │       ├── classify.py
│   │       ├── batch.py
│   │       └── evaluate.py
│   ├── migrations/
│   │   ├── init.sql              # Users table
│   │   └── v2_documents.sql      # Documents + BatchJobs
│   └── tests/                    # 16 pytest tests (mocked LLM)
│
└── docs/technical/
    ├── api-spec.md
    ├── db-schema.md
    └── classifier-design.md      # Prompt strategy + metadata schemas
```

---

## Evaluation

Endpoint `GET /api/v1/evaluate` tính toán từ documents đã được gán nhãn (`ground_truth`):

- **Overall accuracy** — tổng số dự đoán đúng / tổng
- **Per-class F1** — precision × recall / (precision + recall) cho mỗi loại
- **Macro F1** — trung bình F1 tất cả classes

**Target**: accuracy ≥ 90%, per-class F1 ≥ 0.85 cho 6 loại phổ biến nhất.

---

## Design Decisions

**Tại sao không dùng fine-tuned model?**
Zero-shot với Llama 3.3 70B đạt accuracy đủ cao mà không cần labeled training data, không tốn cost fine-tuning, và dễ thêm loại mới bằng cách sửa prompt.

**Tại sao BackgroundTasks thay vì Celery/Redis queue?**
Batch size ≤ 50 files, không cần distributed workers. BackgroundTasks đơn giản hơn, zero infra. Dễ nâng lên Celery khi scale.

**Tại sao Groq thay vì OpenAI?**
Inference nhanh hơn ~10x trên cùng model size, free tier 14.4K tokens/phút đủ cho MVP, không cần credit card.

---

## Deployment

### Backend → Render (Docker)
```bash
# render.yaml đã có sẵn
# Cần set env vars trên Render dashboard:
# DATABASE_URL, REDIS_URL, GROQ_API_KEY
```

### Frontend → Vercel
```bash
# Auto-deploy từ master
# Set: NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com
```

### Database + Redis → AWS Lightsail ($3.50/month)
```bash
ssh user@lightsail-ip
docker compose -f docker-compose.prod.yml up -d
psql $DATABASE_URL -f migrations/init.sql
psql $DATABASE_URL -f migrations/v2_documents.sql
```

---

## License

MIT
