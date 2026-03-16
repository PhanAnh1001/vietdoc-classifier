"""
FastAPI entry point — VietDoc Classifier.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth
from app.routers import classify, batch, evaluate

app = FastAPI(
    title="VietDoc Classifier API",
    version="1.0.0",
    description="Hệ thống phân loại chứng từ kế toán, ngân hàng tiếng Việt bằng AI",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(classify.router, prefix="/api/v1/classify", tags=["classify"])
app.include_router(batch.router, prefix="/api/v1/batch", tags=["batch"])
app.include_router(evaluate.router, prefix="/api/v1/evaluate", tags=["evaluate"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "vietdoc-classifier"}
