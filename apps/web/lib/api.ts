// Single source of HTTP truth for the frontend.

import type {
  FileUploadResponse,
  HealthResponse,
  JobResponse,
  ResultResponse,
  TemplateResponse,
} from "@/types/api";

export const API_BASE =
  (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_BASE) ||
  "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new Error(`API ${res.status}: ${detail}`);
  }
  if (res.status === 204) return undefined as unknown as T;
  return (await res.json()) as T;
}

export async function getHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/api/health");
}

export async function uploadFile(file: File): Promise<FileUploadResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/api/files/upload`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new Error(`Upload failed: ${detail}`);
  }
  return (await res.json()) as FileUploadResponse;
}

export async function getFile(fileId: number): Promise<FileUploadResponse> {
  return apiFetch<FileUploadResponse>(`/api/files/${fileId}`);
}

export async function listTemplates(): Promise<TemplateResponse[]> {
  return apiFetch<TemplateResponse[]>("/api/templates");
}

export async function getTemplate(id: number): Promise<TemplateResponse> {
  return apiFetch<TemplateResponse>(`/api/templates/${id}`);
}

export async function createJob(payload: {
  file_id: number;
  template_id: number;
  input_column: string;
  max_rows: number;
}): Promise<JobResponse> {
  return apiFetch<JobResponse>("/api/jobs", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getJob(jobId: number): Promise<JobResponse> {
  return apiFetch<JobResponse>(`/api/jobs/${jobId}`);
}

export async function retryFailed(jobId: number): Promise<JobResponse> {
  return apiFetch<JobResponse>(`/api/jobs/${jobId}/retry-failed`, { method: "POST" });
}

export async function getJobResults(
  jobId: number,
  status: "all" | "success" | "failed" = "all"
): Promise<ResultResponse[]> {
  return apiFetch<ResultResponse[]>(`/api/jobs/${jobId}/results?status=${status}`);
}

export async function updateResult(
  resultId: number,
  output: Record<string, unknown>
): Promise<ResultResponse> {
  return apiFetch<ResultResponse>(`/api/results/${resultId}`, {
    method: "PATCH",
    body: JSON.stringify({ output }),
  });
}

export function exportUrl(jobId: number, fmt: "csv" | "xlsx"): string {
  return `${API_BASE}/api/jobs/${jobId}/export?format=${fmt}`;
}
