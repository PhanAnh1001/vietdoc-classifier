-- Migration v2: VietDoc Classifier tables
-- Run after init.sql

-- Batch jobs table
CREATE TABLE IF NOT EXISTS batch_jobs (
    id          VARCHAR(36)  PRIMARY KEY DEFAULT gen_random_uuid()::text,
    status      VARCHAR(20)  NOT NULL DEFAULT 'pending',
    total       INTEGER      NOT NULL DEFAULT 0,
    processed   INTEGER      NOT NULL DEFAULT 0,
    failed      INTEGER      NOT NULL DEFAULT 0,
    created_at  TIMESTAMP    WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP    WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_batch_jobs_status ON batch_jobs(status);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id              VARCHAR(36)  PRIMARY KEY DEFAULT gen_random_uuid()::text,
    filename        VARCHAR(500) NOT NULL,
    file_type       VARCHAR(20)  NOT NULL,
    ocr_text        TEXT,
    doc_type        VARCHAR(100),
    confidence      FLOAT,
    metadata        JSONB        DEFAULT '{}',
    ground_truth    VARCHAR(100),
    batch_job_id    VARCHAR(36)  REFERENCES batch_jobs(id) ON DELETE SET NULL,
    status          VARCHAR(20)  NOT NULL DEFAULT 'pending',
    error_msg       TEXT,
    created_at      TIMESTAMP    WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documents_batch_job_id ON documents(batch_job_id);
CREATE INDEX IF NOT EXISTS idx_documents_status       ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_doc_type     ON documents(doc_type);

-- Auto-update updated_at for batch_jobs
CREATE OR REPLACE FUNCTION update_batch_jobs_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER trg_batch_jobs_updated_at
    BEFORE UPDATE ON batch_jobs
    FOR EACH ROW EXECUTE FUNCTION update_batch_jobs_updated_at();
