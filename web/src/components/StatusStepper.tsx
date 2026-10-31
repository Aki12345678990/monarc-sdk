"use client";

import { motion, useReducedMotion } from "motion/react";
import type { JobStatus } from "@/lib/api";
import { JOB_STATUS_LABELS } from "@/lib/labels";
import { DURATION, EASE } from "@/lib/motion";
import { Shimmer } from "./motion/Shimmer";

const SUCCESS_PIPELINE: JobStatus[] = ["awaiting_upload", "queued", "running", "done"];

export function stepperModel(status: JobStatus): {
  steps: JobStatus[];
  active: JobStatus;
  completed: JobStatus[];
} {
  if (status === "awaiting_upload") {
    return { steps: [...SUCCESS_PIPELINE], active: "awaiting_upload", completed: [] };
  }
  if (status === "queued") {
    return { steps: [...SUCCESS_PIPELINE], active: "queued", completed: ["awaiting_upload"] };
  }
  if (status === "running") {
    return { steps: [...SUCCESS_PIPELINE], active: "running", completed: ["awaiting_upload", "queued"] };
  }
  if (status === "done") {
    return { steps: [...SUCCESS_PIPELINE], active: "done", completed: [...SUCCESS_PIPELINE] };
  }
  if (status === "rejected") {
    return { steps: ["awaiting_upload", "rejected"], active: "rejected", completed: ["awaiting_upload"] };
  }
  if (status === "failed") {
    return {
      steps: ["awaiting_upload", "queued", "running", "failed"],
      active: "failed",
      completed: ["awaiting_upload", "queued", "running"],
    };
  }
  return { steps: ["awaiting_upload", "expired"], active: "expired", completed: [] };
}

function Check() {
  return (
    <motion.svg viewBox="0 0 24 24" className="h-4 w-4" aria-hidden>
      <motion.path
        d="M5 12.5 9.5 17 19 7"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: DURATION.base, ease: EASE }}
      />
    </motion.svg>
  );
}

export function StatusStepper({ status, elapsed }: { status: JobStatus; elapsed?: string }) {
  const reduce = useReducedMotion();
  const model = stepperModel(status);
  return (
    <ol className="mt-4 flex flex-wrap gap-3" data-testid="status-stepper">
      {model.steps.map((step) => {
        const done = model.completed.includes(step);
        const active = model.active === step && !done;
        const running = active && step === "running";
        return (
          <li
            key={step}
            data-testid={`step-${step}`}
            data-active={active ? "true" : "false"}
            data-complete={done ? "true" : "false"}
            className={`step-pill ${active ? "step-pill-active" : ""}`}
          >
            {running ? <Shimmer className="pointer-events-none absolute inset-0 rounded-full" /> : null}
            <span className="relative z-[1] flex h-5 w-5 items-center justify-center rounded-full border border-edge-hi">
              {done ? <Check /> : <span className="h-1.5 w-1.5 rounded-full bg-text" />}
            </span>
            <span className="relative z-[1]">{JOB_STATUS_LABELS[step]}</span>
            {running && elapsed ? (
              <span className="relative z-[1] text-sm text-muted" data-testid="step-elapsed">
                {elapsed}
              </span>
            ) : null}
            {active && !running && !reduce ? (
              <motion.span
                aria-hidden
                className="pointer-events-none absolute inset-0 rounded-full border-2 border-accent"
                animate={{ opacity: [0.35, 1, 0.35] }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              />
            ) : null}
          </li>
        );
      })}
    </ol>
  );
}
