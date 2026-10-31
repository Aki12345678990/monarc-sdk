"use client";

import type { ReactNode } from "react";
import { CountUp } from "@/components/motion/CountUp";
import { InfoTooltip } from "@/components/ui/overlay";
import { INDICATOR_STATUS_LABELS } from "@/lib/labels";
import { asArray, asRecord, asString, display, formatPercent1 } from "@/lib/report-access";
import type { Report } from "@/lib/report-types";

function Tile({
  label,
  value,
  extra,
  testId,
  description,
}: {
  label: string;
  value: ReactNode;
  extra?: ReactNode;
  testId: string;
  description?: string;
}) {
  return (
    <div className="tile kpi-tile">
      <p className="flex items-center gap-2 text-sm font-semibold">
        {label}
        {description ? <InfoTooltip label={label} description={description} /> : null}
      </p>
      <p className="kpi mt-1" data-testid={testId}>
        {value}
      </p>
      {extra ? (
        <p className="mt-1 text-sm text-muted" data-testid={`${testId}-percentile`}>
          {extra}
        </p>
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
  const dNote = asString(asRecord(indicators?.D.details).note);

  return (
    <section aria-labelledby="exposure-heading" className="space-y-3">
      <h2 id="exposure-heading" className="section-title">
        Exposure profile
      </h2>
      <div className="kpi-row">
        <Tile
          label="SDK footprint"
          value={counted(dValue, formatPercent1)}
          extra={percentileLine(dPct)}
          testId="tile-d"
          description={dNote ?? undefined}
        />
        <Tile
          label="Distinct SDKs"
          value={counted(sdkValue, (n) => String(Math.round(n)))}
          extra={percentileLine(sdkPct)}
          testId="tile-sdks"
          description="SDK entries attributed by package namespace."
        />
        <Tile
          label="Distinct network hosts"
          value={counted(nValue, (n) => String(Math.round(n)))}
          extra={percentileLine(nPct)}
          testId="tile-n"
          description="Distinct hosts (hosts_distinct_all)"
        />
        <Tile
          label="Frameworks detected"
          value={frameworks.length === 0 ? "None" : frameworks.join(", ")}
          testId="tile-frameworks"
        />
        <div className="tile kpi-tile">
          <p className="text-sm font-semibold">Other indicators</p>
          <ul className="mt-1 space-y-1 text-sm">
            <li data-testid="chip-p">P {INDICATOR_STATUS_LABELS[indicators?.P.status ?? "not_implemented"]}</li>
            <li data-testid="chip-a">A {INDICATOR_STATUS_LABELS[indicators?.A.status ?? "unavailable"]}</li>
            <li data-testid="chip-m">M {INDICATOR_STATUS_LABELS[indicators?.M.status ?? "not_implemented"]}</li>
          </ul>
        </div>
      </div>
    </section>
  );
}
