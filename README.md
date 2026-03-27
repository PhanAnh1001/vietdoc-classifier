# VietDoc Classifier

> Automated classification of Vietnamese accounting and banking documents using AI — accuracy ≥ 90% across 13 document types.

**[Tiếng Việt](README.vi.md)**

Vietnamese enterprises process hundreds of financial documents daily. Manual classification is slow and error-prone at scale. This system automates the workflow using a two-stage LLM pipeline: **Vision OCR → zero-shot classification + structured metadata extraction**.

---

## How It Works

1. Upload a PDF, JPG, or PNG (invoice, payment voucher, bank statement, ...)
2. **OCR**: Groq Llama Vision extracts text from images; pypdf handles text-based PDFs
3. **Classify**: Groq Llama 3.3 70B returns document type + confidence score + extracted metadata
4. Results display immediately — invoice number, date, tax ID, amount pulled automatically

**Batch mode**: upload up to 50 files at once, processed asynchronously with real-time status polling.

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

**Challenge**: the LLM must return a different JSON schema depending on document type — invoices need invoice number, tax ID, VAT breakdown; payroll sheets need period, headcount, totals; etc.

**Solution**: a single prompt with per-type schema hints, `temperature=0.1` for near-deterministic output, and a robust JSON parser that strips markdown fences and falls back to regex extraction.

```python
# classifier_service.py
completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=1024,
    temperature=0.1,   # near-deterministic for classification tasks
)
```

### 13 Supported Document Types

| Key | Vietnamese Name | English |
|-----|-----------------|---------|
| `hoa_don_vat_dau_vao` | Hóa đơn VAT đầu vào | Input VAT invoice |
| `hoa_don_vat_dau_ra` | Hóa đơn VAT đầu ra | Output VAT invoice |
| `phieu_chi` | Phiếu chi | Payment voucher |
| `phieu_thu` | Phiếu thu | Receipt voucher |
| `sao_ke_ngan_hang` | Sao kê ngân hàng | Bank statement |
| `giay_uy_quyen` | Giấy ủy quyền | Authorization letter |
| `thong_bao_cong_no` | Thông báo công nợ | Debt notice |
| `thong_bao_ghi_co` | Thông báo ghi có | Credit advice |
| `bien_lai` | Biên lai | Receipt |
| `hop_dong` | Hợp đồng | Contract |
| `phieu_ke_toan` | Phiếu kế toán | Journal voucher |
| `bang_luong` | Bảng lương | Payroll sheet |
| `khac` | Khác | Other |

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| LLM | Groq Llama 3.3 70B | Fastest inference on market, generous free tier |
| Vision OCR | Groq Llama 3.2 Vision 11B | Multimodal — handles scans and photos |
| PDF OCR | pypdf | Deterministic text extraction, no API call needed |
| Backend | FastAPI (async) | Non-blocking I/O for concurrent file uploads + LLM calls |
| Frontend | Next.js 15 + TypeScript | App Router, strong typing end-to-end |
| Database | PostgreSQL + SQLAlchemy async | Stores history + ground-truth labels for evaluation |
| Queue | FastAPI BackgroundTasks | Zero infra overhead for batch ≤ 50 files |
| Deploy | Vercel + Render + AWS Lightsail | $0 – $3.50/month total |

---

## System Architecture

```
┌─────────────┐    REST/multipart    ┌─────────────┐    async    ┌──────────────────────┐
│   Vercel    │ ───────────────────▶ │   Render    │ ──────────▶ │    AWS Lightsail     │
│  Next.js 15 │                      │   FastAPI   │             │  PostgreSQL + Redis  │
└─────────────┘                      └──────┬──────┘             └──────────────────────┘
                                            │ HTTP
                                            ▼
                                     ┌─────────────┐
                                     │  Groq Cloud │
                                     │ Llama Vision│
                                     │  Llama 3.3  │
                                     └─────────────┘
```

---

## Quick Start

**Requirements**: Docker, Docker Compose, [Groq API key](https://console.groq.com) (free)

```bash
git clone https://github.com/PhanAnh1001/vietdoc-classifier
cd vietdoc-classifier

# Configure environment
cp .env.example .env
# Fill in GROQ_API_KEY in .env

# Start all services (PostgreSQL + Redis + Backend + Frontend)
docker compose up -d

# Run DB migrations
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
GET  /api/v1/batch/{job_id}    Poll batch status + per-file results
GET  /api/v1/evaluate          Accuracy + per-class F1 from labeled documents
GET  /health
```

Full spec: [`docs/technical/api-spec.md`](docs/technical/api-spec.md)

---

## Development

### Backend (FastAPI)
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload   # http://localhost:8000

# Run tests (19 tests, SQLite in-memory, no Groq key required)
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

## Project Structure

```
├── app/                              # Next.js 15 frontend
│   └── src/
│       ├── app/(dashboard)/
│       │   ├── classify/             # Single file upload + result card
│       │   ├── batch/                # Batch upload + real-time polling
│       │   └── evaluate/             # Accuracy / F1 metrics dashboard
│       ├── components/classify/      # ClassifyResult component
│       └── lib/api.ts                # Fully-typed API client
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
│   │   ├── init.sql                  # Users table
│   │   └── v2_documents.sql          # Documents + BatchJobs tables
│   └── tests/                        # 19 pytest tests (LLM mocked)
│
└── docs/technical/
    ├── api-spec.md
    ├── db-schema.md
    └── classifier-design.md          # Prompt strategy + metadata schemas
```

---

## Evaluation

`GET /api/v1/evaluate` computes metrics against documents with a `ground_truth` label:

- **Overall accuracy** — correct predictions / total
- **Per-class F1** — harmonic mean of precision and recall per document type
- **Macro F1** — unweighted average F1 across all classes

**Targets**: accuracy ≥ 90%, per-class F1 ≥ 0.85 for the 6 most common document types.

---

## Design Decisions

**Why zero-shot instead of a fine-tuned model?**
Llama 3.3 70B achieves sufficient accuracy out of the box with no labeled training data, no fine-tuning cost, and adding a new document type is as simple as updating the prompt — no retraining cycle.

**Why FastAPI BackgroundTasks instead of Celery + Redis queue?**
Batch size is capped at 50 files; distributed workers would be overkill. BackgroundTasks requires zero additional infrastructure. The codebase can be upgraded to Celery later with a single service swap.

**Why Groq instead of OpenAI?**
~10× faster inference on equivalent model sizes, 14,400 tokens/min free tier sufficient for MVP, and no credit card required to get started.

---

## Deployment

### Backend → Render (Docker)
```bash
# render.yaml is pre-configured
# Set these env vars in the Render dashboard:
# DATABASE_URL, REDIS_URL, GROQ_API_KEY
```

### Frontend → Vercel
```bash
# Auto-deploys from master branch
# Set: NEXT_PUBLIC_API_URL=https://your-service.onrender.com
```

### Database + Redis → AWS Lightsail ($3.50/month)
```bash
ssh user@<lightsail-ip>
docker compose -f docker-compose.prod.yml up -d
psql $DATABASE_URL -f migrations/init.sql
psql $DATABASE_URL -f migrations/v2_documents.sql
```

---

## License

MIT
