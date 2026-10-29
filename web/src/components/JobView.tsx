"use client";

import { AnimatePresence, motion } from "motion/react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { ApiError, fetchReportText, getJob, TERMINAL_STATUSES, type JobResponse } from "@/lib/api";
import { messageForErrorCode } from "@/lib/error-messages";
import { jobStatusLabel } from "@/lib/labels";
import { DURATION, EASE } from "@/lib/motion";
import type { Report } from "@/lib/report-types";
import { ScanCard } from "./ScanCard";
import { StatusStepper } from "./StatusStepper";
import { ReportView } from "./report/ReportView";

const POLL_MS = 2000;

function formatElapsed(ms: number): string {
  const total = Math.max(0, Math.floor(ms / 1000));
  const minutes = Math.floor(total / 60);
  const seconds = total % 60;
  return minutes > 0 ? `${minutes} min ${seconds} s` : `${seconds} s`;
}

export function JobView({ jobId }: { jobId: string }) {
  const [job, setJob] = useState<JobResponse | null>(null);
  const [pollError, setPollError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [loaded, setLoaded] = useState<{ report: Report; json: string } | null>(null);
  const [reportError, setReportError] = useState<string | null>(null);
  const [now, setNow] = useState<number | null>(null);

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | undefined;

    async function poll() {
      try {
        const next = await getJob(jobId);
        if (cancelled) return;
        setJob(next);
        setPollError(null);
        if (TERMINAL_STATUSES.includes(next.status)) return;
      } catch (caught) {
        if (cancelled) return;
        if (caught instanceof ApiError && caught.status === 404) {
          setNotFound(true);
          return;
        }
        setPollError("Could not reach the API. Retrying…");
      }
      timer = setTimeout(poll, POLL_MS);
    }

    void poll();
    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [jobId]);

  const running = job?.status === "running";
  useEffect(() => {
    if (!running) return;
    const interval = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(interval);
  }, [running]);

  const reportUrl = job?.status === "done" ? job.report_url : null;
  useEffect(() => {
    if (!reportUrl) return;
    let cancelled = false;
    fetchReportText(reportUrl)
      .then((json) => {
        if (!cancelled) setLoaded({ report: JSON.parse(json) as Report, json });
      })
      .catch((caught: unknown) => {
        if (!cancelled) {
          setReportError(
            caught instanceof Error ? caught.message : "The report could not be loaded.",
          );
        }
      });
    return () => {
      cancelled = true;
    };
  }, [reportUrl]);

  const startedAt = job ? Date.parse(job.updated_at) : NaN;

  return (
    <div className="space-y-6">
      <section aria-labelledby="job-heading" className="card">
        <h1 id="job-heading" className="text-3xl">
          Analysis job
        </h1>
        <p className="mt-1 font-mono text-sm break-all">{jobId}</p>
        <div role="status" aria-live="polite" className="mt-3">
          {notFound ? (
            <p>This job was not found.</p>
          ) : job ? (
            <AnimatePresence mode="wait">
              <motion.div
                key={job.status}
                initial={{ opacity: 0.6 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: DURATION.fast, ease: EASE }}
              >
                <p className="text-xl">
                  Status: <span className="font-semibold">{jobStatusLabel(job.status)}</span>
                </p>
                <StatusStepper status={job.status} />
                {running && now !== null && Number.isFinite(startedAt) ? (
                  <ScanCard elapsed={formatElapsed(now - startedAt)} />
                ) : null}
              </motion.div>
            </AnimatePresence>
          ) : (
            <p>Loading job status…</p>
          )}
          {pollError ? <p>{pollError}</p> : null}
        </div>

        {job?.status === "rejected" || job?.status === "failed" ? (
          <div className="mt-3 space-y-1">
            <p>{messageForErrorCode(job.error_code)}</p>
            <p className="text-sm">
              Error code: <code>{job.error_code ?? "—"}</code>
            </p>
            {job.error_message ? (
              <p className="text-sm">Details: {job.error_message}</p>
            ) : null}
          </div>
        ) : null}

        {job?.status === "expired" ? (
          <p className="mt-3">
            No file arrived before the upload window closed. Start again from the upload page.
          </p>
        ) : null}

        {job && TERMINAL_STATUSES.includes(job.status) && job.status !== "done" ? (
          <p className="mt-3">
            <Link href="/">Upload another APK</Link>
          </p>
        ) : null}
      </section>

      {reportError ? <p role="alert">The report could not be loaded: {reportError}</p> : null}
      {loaded ? <ReportView report={loaded.report} json={loaded.json} /> : null}
    </div>
  );
}
