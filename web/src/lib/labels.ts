import type { JobStatus } from "./api";
import type { IndicatorResult } from "./report-types";

export const JOB_STATUS_LABELS: Record<JobStatus, string> = {
  awaiting_upload: "Waiting for upload",
  queued: "Queued",
  running: "Analysing",
  done: "Done",
  rejected: "Rejected",
  failed: "Failed",
  expired: "Expired",
};

export const INDICATOR_STATUS_LABELS: Record<IndicatorResult["status"], string> = {
  ok: "OK",
  unavailable: "Unavailable",
  not_implemented: "Not implemented",
};

export function jobStatusLabel(status: string): string {
  return (JOB_STATUS_LABELS as Record<string, string>)[status] ?? status;
}
