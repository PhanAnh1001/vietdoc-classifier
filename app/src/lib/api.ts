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
