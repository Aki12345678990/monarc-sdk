"use client";

import { useState } from "react";
import type { Report } from "@/lib/report-types";
import { display, formatBytes } from "@/lib/report-access";

export function ReportHeader({ report }: { report: Report }) {
  const input = report.input ?? {};
  const sha256 = input.sha256 ?? null;
  const [copied, setCopied] = useState(false);

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
            <button type="button" onClick={copySha} className="btn-secondary text-sm">
              {copied ? "Copied" : "Copy SHA-256"}
            </button>
          ) : null}
        </dd>
      </dl>
    </section>
  );
}
