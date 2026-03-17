// API client for communicating with the FastAPI backend

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string,
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }

  return res.json();
}

async function uploadFile<T>(path: string, formData: FormData): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }

  return res.json();
}

// Health check
export function getHealth() {
  return request<{ status: string }>("/health");
}

// Auth
export function login(email: string, password: string) {
  return request<{ access_token: string; token_type: string }>(
    "/api/v1/auth/login",
    {
      method: "POST",
      body: JSON.stringify({ email, password }),
    },
  );
}

export function register(email: string, password: string, fullName?: string) {
  return request<{ id: string; email: string }>(
    "/api/v1/auth/register",
    {
      method: "POST",
      body: JSON.stringify({ email, password, full_name: fullName }),
    },
  );
}

// ── Classify ──────────────────────────────────────────────────────────────

export interface ClassifyResult {
  id: string;
  filename: string;
  doc_type: string;
  doc_type_label: string;
  confidence: number;
  ocr_text: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export function classifyDocument(file: File): Promise<ClassifyResult> {
  const formData = new FormData();
  formData.append("file", file);
  return uploadFile<ClassifyResult>("/api/v1/classify", formData);
}

// ── Batch ─────────────────────────────────────────────────────────────────

export interface BatchJobResponse {
  job_id: string;
  status: string;
  total: number;
  processed: number;
  failed: number;
  created_at: string;
}

export interface BatchDocumentResult {
  id: string;
  filename: string;
  doc_type: string | null;
  doc_type_label: string | null;
  confidence: number | null;
  metadata: Record<string, unknown>;
  status: string;
  error_msg: string | null;
}

export interface BatchJobDetail extends BatchJobResponse {
  results: BatchDocumentResult[];
  updated_at: string;
}

export function createBatch(files: File[]): Promise<BatchJobResponse> {
  const formData = new FormData();
  files.forEach((f) => formData.append("files", f));
  return uploadFile<BatchJobResponse>("/api/v1/batch", formData);
}

export function getBatchStatus(jobId: string): Promise<BatchJobDetail> {
  return request<BatchJobDetail>(`/api/v1/batch/${jobId}`);
}

// ── Evaluate ──────────────────────────────────────────────────────────────

export interface EvaluateResult {
  total_evaluated: number;
  accuracy: number;
  per_class_f1: Record<string, number>;
  macro_f1: number;
  confusion_counts: Record<string, { correct: number; total: number }>;
}

export function getEvaluationMetrics(
  limit = 100,
): Promise<EvaluateResult> {
  return request<EvaluateResult>(`/api/v1/evaluate?limit=${limit}`);
}
