import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Float, Integer, JSON
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)


class BatchJob(Base):
    __tablename__ = "batch_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String(20), default="pending", nullable=False)  # pending/processing/done/failed
    total = Column(Integer, default=0)
    processed = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False)  # jpg/png/pdf
    ocr_text = Column(Text)
    doc_type = Column(String(100))
    confidence = Column(Float)
    metadata_ = Column("metadata", JSON, default=dict)
    ground_truth = Column(String(100))  # for evaluation
    batch_job_id = Column(String(36), ForeignKey("batch_jobs.id"), nullable=True)
    status = Column(String(20), default="pending")  # pending/processing/done/failed
    error_msg = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
