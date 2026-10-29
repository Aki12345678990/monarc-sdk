"use client";

import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";
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

export function ReportHeader({ report }: { report: Report }) {
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
    <section aria-labelledby="report-heading" className="card">
      <h1 id="report-heading" className="text-3xl break-all">
        {display(input.package_name)}
      </h1>
      <dl className="mt-3 grid grid-cols-[max-content_1fr] gap-x-4 gap-y-1">
        <dt className="font-semibold">Version</dt>
        <dd>
          {display(input.version_name)} (version code {display(input.version_code)})
        </dd>
        <dt className="font-semibold">Min SDK</dt>
        <dd>{display(input.min_sdk)}</dd>
        <dt className="font-semibold">Target SDK</dt>
        <dd>{display(input.target_sdk)}</dd>
        <dt className="font-semibold">File size</dt>
        <dd>{formatBytes(input.file_size)}</dd>
        <dt className="font-semibold">SHA-256</dt>
        <dd className="flex flex-wrap items-center gap-2">
          <code className="break-all">{display(sha256)}</code>
          {sha256 ? (
            <button type="button" onClick={copySha} className="btn-secondary inline-flex items-center gap-2 text-sm">
              <AnimatePresence mode="wait">{copied ? <CheckIcon /> : <CopyIcon />}</AnimatePresence>
              {copied ? "Copied" : "Copy SHA-256"}
            </button>
          ) : null}
        </dd>
      </dl>
    </section>
  );
}
