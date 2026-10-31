"use client";

import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState, type ReactNode } from "react";
import { DURATION, EASE } from "@/lib/motion";
import { display, formatBytes } from "@/lib/report-access";
import type { Report } from "@/lib/report-types";

function CopyIcon() {
  return (
    <motion.svg key="copy" viewBox="0 0 24 24" className="h-4 w-4" aria-hidden initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.8, opacity: 0 }} transition={{ duration: DURATION.fast, ease: EASE }}>
      <rect x="8" y="8" width="12" height="12" rx="1.5" fill="none" stroke="currentColor" strokeWidth="2" />
      <path d="M4 16V5.5A1.5 1.5 0 0 1 5.5 4H16" fill="none" stroke="currentColor" strokeWidth="2" />
    </motion.svg>
  );
}

function CheckIcon() {
  return (
    <motion.svg key="check" viewBox="0 0 24 24" className="h-4 w-4" aria-hidden initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.8, opacity: 0 }} transition={{ duration: DURATION.fast, ease: EASE }}>
      <motion.path
        d="M5 12.5 9.5 17 19 7"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: DURATION.base, ease: EASE }}
      />
    </motion.svg>
  );
}

function truncateSha(value: string): string {
  return value.length <= 16 ? value : `${value.slice(0, 8)}…${value.slice(-4)}`;
}

export function ReportHeader({
  report,
  analysedAt,
  actions,
}: {
  report: Report;
  analysedAt?: string | null;
  actions?: ReactNode;
}) {
  const input = report.input ?? {};
  const sha256 = input.sha256 ?? null;
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!copied) return;
    const timer = setTimeout(() => setCopied(false), 1500);
    return () => clearTimeout(timer);
  }, [copied]);

  async function copySha() {
    if (!sha256) return;
    try {
      await navigator.clipboard.writeText(sha256);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }

  return (
    <section aria-labelledby="report-heading" className="card identity-bar">
      <div className="identity-meta">
        <h1 id="report-heading" className="m-0 font-mono text-sm break-all">
          {display(input.package_name)}
        </h1>
        <span>{display(input.version_name)}</span>
        <span>{formatBytes(input.file_size)}</span>
        <span className="inline-flex items-center gap-1 font-mono">
          <code title={sha256 ?? undefined}>{sha256 ? truncateSha(sha256) : display(sha256)}</code>
          {sha256 ? (
            <button type="button" onClick={copySha} className="btn-secondary inline-flex items-center gap-1 text-sm">
              <AnimatePresence mode="wait">{copied ? <CheckIcon /> : <CopyIcon />}</AnimatePresence>
              <span>{copied ? "Copied" : "Copy"}</span>
            </button>
          ) : null}
        </span>
        <span>{analysedAt ? analysedAt : "—"}</span>
        <span>{display(report.engine?.version)}</span>
      </div>
      <div className="identity-actions">{actions}</div>
    </section>
  );
}
