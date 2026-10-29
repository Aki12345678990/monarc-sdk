"use client";

import { motion } from "motion/react";
import type { ReactNode } from "react";
import { CountUp } from "@/components/motion/CountUp";
import { INDICATOR_STATUS_LABELS } from "@/lib/labels";
import { SPRING } from "@/lib/motion";
import { asArray, asRecord, asString, display, formatPercent1 } from "@/lib/report-access";
import type { Report } from "@/lib/report-types";

function Tile({
  label,
  value,
  extra,
  testId,
  bar,
}: {
  label: string;
  value: ReactNode;
  extra?: ReactNode;
  testId: string;
  bar?: number | null;
}) {
  return (
    <div className="card">
      <p className="text-sm font-semibold">{label}</p>
      <p className="mt-1 text-3xl" data-testid={testId}>
        {value}
      </p>
      {extra ? (
        <p className="mt-1 text-sm" data-testid={`${testId}-percentile`}>
          {extra}
        </p>
      ) : null}
      {typeof bar === "number" ? (
        <div className="mt-2 h-1 overflow-hidden rounded bg-charcoal/15">
          <motion.div
            className="h-full origin-left bg-orange"
            initial={{ scaleX: 0 }}
            animate={{ scaleX: Math.min(Math.max(bar / 100, 0), 1) }}
            transition={SPRING}
          />
        </div>
      ) : null}
    </div>
  );
}

function percentileLine(value: number | null): ReactNode {
  if (value === null) return null;
  return (
    <>
      higher than <CountUp value={value} format={(n) => n.toFixed(1)} />% of corpus apps
    </>
  );
}

function counted(value: number | null, format: (n: number) => string): ReactNode {
  if (value === null) return display(value);
  return <CountUp value={value} format={format} />;
}

export function ExposureProfile({ report }: { report: Report }) {
  const indicators = report.indicators;
  const comparison = report.comparison;
  const frameworks = asArray(report.frameworks)
    .map(asRecord)
    .map((item) => asString(item.name))
    .filter((name): name is string => name !== null);
  const dValue = typeof indicators?.D.value === "number" ? indicators.D.value : null;
  const nValue = typeof indicators?.N.value === "number" ? indicators.N.value : null;
  const sdkValue =
    typeof asRecord(indicators?.D.details).n_sdk_distinct === "number"
      ? (asRecord(indicators?.D.details).n_sdk_distinct as number)
      : null;
  const dPct = comparison?.metrics.D?.percentile ?? null;
  const nPct = comparison?.metrics.N?.percentile ?? null;
  const sdkPct = comparison?.metrics.n_sdk_distinct?.percentile ?? null;

  return (
    <section aria-labelledby="exposure-heading" className="space-y-3">
      <h2 id="exposure-heading" className="text-2xl">
        Exposure profile
      </h2>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <Tile
          label="SDK footprint"
          value={counted(dValue, formatPercent1)}
          extra={percentileLine(dPct)}
          testId="tile-d"
          bar={dPct}
        />
        <Tile
          label="Distinct SDKs"
          value={counted(sdkValue, (n) => String(Math.round(n)))}
          extra={percentileLine(sdkPct)}
          testId="tile-sdks"
          bar={sdkPct}
        />
        <Tile
          label="Distinct network hosts"
          value={counted(nValue, (n) => String(Math.round(n)))}
          extra={percentileLine(nPct)}
          testId="tile-n"
          bar={nPct}
        />
        <Tile
          label="Frameworks detected"
          value={frameworks.length === 0 ? "None" : frameworks.join(", ")}
          testId="tile-frameworks"
        />
        <div className="card">
          <p className="text-sm font-semibold">Other indicators</p>
          <ul className="mt-2 space-y-1 text-sm">
            <li data-testid="chip-p">P {INDICATOR_STATUS_LABELS[indicators?.P.status ?? "not_implemented"]}</li>
            <li data-testid="chip-a">A {INDICATOR_STATUS_LABELS[indicators?.A.status ?? "unavailable"]}</li>
            <li data-testid="chip-m">M {INDICATOR_STATUS_LABELS[indicators?.M.status ?? "not_implemented"]}</li>
          </ul>
        </div>
      </div>
      <p className="text-sm" data-testid="exposure-caption">
        {comparison
          ? `${comparison.corpus.description} Percentile compares this app with the corpus one measure at a time. It is not a risk measure.`
          : (report.comparison_reason ?? "—")}
      </p>
    </section>
  );
}
