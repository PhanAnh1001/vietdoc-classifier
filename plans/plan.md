## Trạng thái hiện tại
Phase: Core implementation | Branch: claude/vietdoc-classifier-plan-dHsm0

## TODO
- [ ] Backend: implement OCR + classifier + batch services
- [ ] Backend: routers classify/batch/evaluate
- [ ] Backend: DB migration v2 (documents, batch_jobs)
- [ ] Frontend: classify page (upload + result)
- [ ] Frontend: batch page (multi-upload + status polling)
- [ ] Frontend: update dashboard nav + home page
- [ ] Tests: backend pytest cho classify/batch/evaluate
- [ ] Deploy: set GROQ_API_KEY trên Render + Vercel

## Notes
- Frontend: Next.js 15 on Vercel
- Backend: FastAPI on Render (Docker)
- DB + Redis: AWS Lightsail
- API base: /api/v1/
- LLM: Groq Llama 3.3 70B (llama-3.3-70b-versatile) cho classify
- OCR: Groq Llama Vision (llama-3.2-11b-vision-preview) cho image
- PDF: pypdf text extraction
- 12 document types: xem docs/technical/classifier-design.md
- Groq SDK: `from groq import Groq` (sync) / AsyncGroq (async)
- Batch: FastAPI BackgroundTasks + DB status tracking
- Evaluate: accuracy/F1 từ labeled test set trong DB

## Lịch sử (milestone)
- Project template initialized
- VietDoc-Classifier plan + technical design created
