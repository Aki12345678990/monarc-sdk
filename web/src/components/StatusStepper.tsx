"use client";

import { motion, useReducedMotion } from "motion/react";
import type { JobStatus } from "@/lib/api";
import { DURATION, EASE, EASE_LOOP, LOOP } from "@/lib/motion";

const PIPELINE = ["upload", "queued", "analysing", "done"] as const;
type PipelineStep = (typeof PIPELINE)[number];

const LABELS: Record<PipelineStep | "rejected" | "failed" | "expired", string> = {
  upload: "Upload",
  queued: "Queued",
  analysing: "Analysing",
  done: "Done",
  rejected: "Rejected",
  failed: "Failed",
  expired: "Expired",
};

export function stepperModel(status: JobStatus): {
  steps: Array<PipelineStep | "rejected" | "failed" | "expired">;
  active: string;
  completed: string[];
} {
  if (status === "awaiting_upload") {
    return { steps: [...PIPELINE], active: "upload", completed: [] };
  }
  if (status === "queued") {
    return { steps: [...PIPELINE], active: "queued", completed: ["upload"] };
  }
  if (status === "running") {
    return { steps: [...PIPELINE], active: "analysing", completed: ["upload", "queued"] };
  }
  if (status === "done") {
    return { steps: [...PIPELINE], active: "done", completed: ["upload", "queued", "analysing", "done"] };
  }
  if (status === "rejected") {
    return { steps: ["upload", "rejected"], active: "rejected", completed: ["upload"] };
  }
  if (status === "failed") {
    return {
      steps: ["upload", "queued", "analysing", "failed"],
      active: "failed",
      completed: ["upload", "queued", "analysing"],
    };
  }
  return { steps: ["upload", "expired"], active: "expired", completed: [] };
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

export function StatusStepper({ status }: { status: JobStatus }) {
  const reduce = useReducedMotion();
  const model = stepperModel(status);
  return (
    <ol className="mt-4 flex flex-wrap gap-3" data-testid="status-stepper">
      {model.steps.map((step) => {
        const done = model.completed.includes(step);
        const active = model.active === step && !done;
        return (
          <li
            key={step}
            data-testid={`step-${step}`}
            data-active={active ? "true" : "false"}
            data-complete={done ? "true" : "false"}
            className={`step-pill ${active ? "step-pill-active" : ""}`}
          >
            {active ? (
              <motion.span
                aria-hidden
                className="pointer-events-none absolute inset-0 rounded-full border-2 border-accent"
                animate={reduce ? { opacity: 1 } : { opacity: [0.35, 1, 0.35] }}
                transition={
                  reduce
                    ? { duration: 0 }
                    : { duration: LOOP.breathe, repeat: Infinity, ease: EASE_LOOP }
                }
              />
            ) : null}
            <span className="relative z-[1] flex h-5 w-5 items-center justify-center rounded-full border border-edge-hi">
              {done ? <Check /> : <span className="h-1.5 w-1.5 rounded-full bg-text" />}
            </span>
            <span className="relative z-[1]">{LABELS[step]}</span>
          </li>
        );
      })}
    </ol>
  );
}
