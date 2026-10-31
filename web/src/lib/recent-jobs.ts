const KEY = "monarc-recent-jobs";

export type RecentJob = { id: string; label: string; at: string };

export function readRecentJobs(): RecentJob[] {
  if (typeof localStorage === "undefined") return [];
  try {
    const raw = localStorage.getItem(KEY);
    const parsed = raw ? (JSON.parse(raw) as unknown) : [];
    return Array.isArray(parsed) ? (parsed as RecentJob[]) : [];
  } catch {
    return [];
  }
}

export function rememberRecentJob(id: string, label: string): void {
  if (typeof localStorage === "undefined") return;
  const next = [{ id, label, at: new Date().toISOString() }, ...readRecentJobs().filter((job) => job.id !== id)].slice(
    0,
    8,
  );
  localStorage.setItem(KEY, JSON.stringify(next));
}
