export const API_BASE = (process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000").replace(/\/+$/, "");

export type JobStatus =
  | "awaiting_upload"
  | "queued"
  | "running"
  | "done"
  | "rejected"
  | "failed"
  | "expired";

export const TERMINAL_STATUSES: readonly JobStatus[] = ["done", "rejected", "failed", "expired"];

export interface CreateJobResponse {
  job_id: string;
  upload_url: string;
  upload_method: "PUT";
  max_bytes: number;
  expires_at: string;
}

export interface JobResponse {
  job_id: string;
  status: JobStatus;
  error_code: string | null;
  error_message: string | null;
  sha256: string | null;
  file_size: number | null;
  created_at: string;
  updated_at: string;
  report_url: string | null;
}

export function apiUrl(path: string): string {
  return `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
}

export class ApiError extends Error {
  constructor(readonly status: number) {
    super(`API responded with HTTP ${status}`);
  }
}

async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) throw new ApiError(response.status);
  return (await response.json()) as T;
}

export async function createJob(filename: string): Promise<CreateJobResponse> {
  const response = await fetch(apiUrl("/api/jobs"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filename }),
  });
  return readJson<CreateJobResponse>(response);
}

export async function getJob(jobId: string): Promise<JobResponse> {
  const response = await fetch(apiUrl(`/api/jobs/${encodeURIComponent(jobId)}`), {
    cache: "no-store",
  });
  return readJson<JobResponse>(response);
}

export async function fetchReportText(reportUrl: string): Promise<string> {
  const response = await fetch(apiUrl(reportUrl), { cache: "no-store" });
  if (!response.ok) throw new ApiError(response.status);
  return response.text();
}

/** PUT the file straight to the API with XMLHttpRequest so upload progress is observable. */
export function uploadFile(
  uploadUrl: string,
  file: File,
  onProgress: (loaded: number, total: number) => void,
): Promise<number> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("PUT", apiUrl(uploadUrl));
    xhr.setRequestHeader("Content-Type", "application/octet-stream");
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) onProgress(event.loaded, event.total);
    };
    xhr.onload = () => resolve(xhr.status);
    xhr.onerror = () => reject(new Error("Network error during upload."));
    xhr.onabort = () => reject(new Error("Upload aborted."));
    xhr.send(file);
  });
}
