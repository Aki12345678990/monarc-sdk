"use client";

import { motion } from "motion/react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useId, useState, useSyncExternalStore, type DragEvent, type FormEvent } from "react";
import { createJob, uploadFile } from "@/lib/api";
import { DURATION, EASE, SPRING } from "@/lib/motion";
import { readRecentJobs } from "@/lib/recent-jobs";
import { formatBytes } from "@/lib/report-access";

type Phase = "idle" | "creating" | "uploading" | "redirecting";

export function UploadForm() {
  const router = useRouter();
  const inputId = useId();
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [phase, setPhase] = useState<Phase>("idle");
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const busy = phase !== "idle";

  function choose(candidate: File | null) {
    setError(null);
    setProgress(0);
    if (candidate && !candidate.name.toLowerCase().endsWith(".apk")) {
      setFile(null);
      setError("Please choose a file with the .apk extension.");
      return;
    }
    setFile(candidate);
  }

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragging(false);
    if (busy) return;
    choose(event.dataTransfer.files?.[0] ?? null);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file || busy) return;
    setError(null);
    setPhase("creating");
    try {
      const job = await createJob(file.name);
      if (file.size > job.max_bytes) {
        setError(
          `This file is ${formatBytes(file.size)}; the upload limit is ${formatBytes(job.max_bytes)}.`,
        );
        setPhase("idle");
        return;
      }
      setPhase("uploading");
      const status = await uploadFile(job.upload_url, file, (loaded, total) =>
        setProgress(total > 0 ? Math.round((loaded / total) * 100) : 0),
      );
      if (status === 200) {
        setProgress(100);
        setPhase("redirecting");
        router.push(`/jobs/${job.job_id}`);
        return;
      }
      const reasons: Record<number, string> = {
        409: "This upload slot was already used.",
        410: "The upload window expired. Please try again.",
        413: "The file is larger than the upload limit.",
      };
      setError(reasons[status] ?? `The upload failed (HTTP ${status}).`);
      setPhase("idle");
    } catch (caught) {
      setError(
        caught instanceof Error
          ? `${caught.message} Is the API running?`
          : "The upload failed. Is the API running?",
      );
      setPhase("idle");
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4" aria-describedby={`${inputId}-help`}>
      <motion.div
        onDragOver={(event) => {
          event.preventDefault();
          if (!busy) setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        animate={{ scale: dragging ? 1.01 : 1 }}
        transition={{ duration: DURATION.fast, ease: EASE }}
        className={`panel dropzone ${dragging ? "is-over" : ""}`}
      >
        <span className="dropzone-ring" aria-hidden />
        <p className="mb-3">Drag and drop an APK here, or choose a file.</p>
        <label htmlFor={inputId} className="mb-2 block font-semibold">
          APK file
        </label>
        <input
          id={inputId}
          type="file"
          accept=".apk"
          disabled={busy}
          onChange={(event) => choose(event.target.files?.[0] ?? null)}
          className="mx-auto block text-sm file:mr-3 file:cursor-pointer file:rounded file:border-0 file:bg-bg-2 file:px-3 file:py-2 file:text-text"
        />
        <p id={`${inputId}-help`} className="mt-2 text-sm">
          {file ? (
            <span className="chip font-mono">
              Selected: {file.name} ({formatBytes(file.size)})
            </span>
          ) : (
            "No file selected."
          )}
        </p>
      </motion.div>

      <button type="submit" disabled={!file || busy} className="btn-primary">
        {phase === "creating"
          ? "Creating job…"
          : phase === "uploading"
            ? "Uploading…"
            : phase === "redirecting"
              ? "Opening job…"
              : "Upload and analyse"}
      </button>

      {phase === "uploading" || phase === "redirecting" ? (
        <div>
          <div
            role="progressbar"
            aria-label="Upload progress"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={progress}
            className="progress-track"
          >
            <motion.div
              className="progress-fill"
              initial={{ scaleX: 0 }}
              animate={{ scaleX: progress / 100 }}
              transition={SPRING}
            />
          </div>
          <p className="mt-1 text-sm">
            {progress}% uploaded
          </p>
        </div>
      ) : null}

      <p role="alert" aria-live="assertive" className="min-h-6">
        {error}
      </p>
    </form>
  );
}

function subscribeRecent(onStoreChange: () => void) {
  if (typeof window === "undefined") return () => {};
  window.addEventListener("storage", onStoreChange);
  return () => window.removeEventListener("storage", onStoreChange);
}

export function RecentAnalyses() {
  const jobs = useSyncExternalStore(subscribeRecent, readRecentJobs, () => []);
  if (jobs.length === 0) return null;
  return (
    <section aria-labelledby="recent-heading" className="card span-12">
      <h2 id="recent-heading" className="section-title">
        Your recent analyses
      </h2>
      <ul className="mt-2 space-y-1">
        {jobs.map((job) => (
          <li key={job.id}>
            <Link href={`/jobs/${job.id}`} className="font-mono text-sm">
              {job.label}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
