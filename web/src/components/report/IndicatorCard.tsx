"use client";

import { motion } from "motion/react";
import type { ReactNode } from "react";
import { INDICATOR_STATUS_LABELS } from "@/lib/labels";
import { DURATION, EASE } from "@/lib/motion";
import type { IndicatorResult } from "@/lib/report-types";

export function IndicatorCard({
  letter,
  title,
  indicator,
  children,
}: {
  letter: string;
  title: string;
  indicator: IndicatorResult | undefined;
  children?: ReactNode;
}) {
  const headingId = `indicator-${letter}`;
  return (
    <motion.section
      aria-labelledby={headingId}
      className="card"
      whileHover={{ y: -2, borderColor: "var(--border-strong)" }}
      transition={{ duration: DURATION.fast, ease: EASE }}
    >
      <h2 id={headingId} className="text-2xl">
        {letter} — {title}
      </h2>
      <dl className="mt-2 grid grid-cols-[max-content_1fr] gap-x-4 gap-y-1 text-sm">
        <dt className="font-semibold">Status</dt>
        <dd data-testid={`indicator-${letter}-status`}>
          {indicator ? INDICATOR_STATUS_LABELS[indicator.status] ?? indicator.status : "—"}
        </dd>
        {indicator?.reason ? (
          <>
            <dt className="font-semibold">Reason</dt>
            <dd>{indicator.reason}</dd>
          </>
        ) : null}
        {indicator?.definition_source ? (
          <>
            <dt className="font-semibold">Definition source</dt>
            <dd className="font-mono">{indicator.definition_source}</dd>
          </>
        ) : null}
      </dl>
      {children ? <div className="mt-4">{children}</div> : null}
    </motion.section>
  );
}
