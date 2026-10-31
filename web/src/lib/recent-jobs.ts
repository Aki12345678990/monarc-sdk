const KEY = "monarc-recent-jobs";

export type RecentJob = { id: string; label: string; at: string };

const EMPTY: RecentJob[] = [];
let cachedRaw: string | null | undefined;
let cached: RecentJob[] = EMPTY;

export function readRecentJobs(): RecentJob[] {
  if (typeof localStorage === "undefined") return EMPTY;
  try {
    const raw = localStorage.getItem(KEY);
    if (raw === cachedRaw) return cached;
    cachedRaw = raw;
    const parsed = raw ? (JSON.parse(raw) as unknown) : [];
    cached = Array.isArray(parsed) ? (parsed as RecentJob[]) : EMPTY;
    return cached;
  } catch {
    return EMPTY;
  }
}

export function rememberRecentJob(id: string, label: string): void {
  if (typeof localStorage === "undefined") return;
  const next = [{ id, label, at: new Date().toISOString() }, ...readRecentJobs().filter((job) => job.id !== id)].slice(
    0,
    8,
  );
  const raw = JSON.stringify(next);
  localStorage.setItem(KEY, raw);
  cachedRaw = raw;
  cached = next;
}
