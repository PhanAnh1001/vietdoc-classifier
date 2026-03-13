"""
FastAPI entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, items

app = FastAPI(
    title="My App API",
    version="0.1.0",
    description="Backend API template — Next.js + FastAPI + PostgreSQL",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(items.router, prefix="/api/v1/items", tags=["items"])


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "my-app-backend"}
