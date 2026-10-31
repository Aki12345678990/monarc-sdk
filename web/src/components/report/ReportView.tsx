"use client";

import { useRef, useState } from "react";
import { AboutSheet, Tabs } from "@/components/ui/overlay";
import type { Report } from "@/lib/report-types";
import { display, formatPercent1 } from "@/lib/report-access";
import { ApisA } from "./ApisA";
import { CorpusPosition } from "./CorpusPosition";
import { DownloadJson } from "./DownloadJson";
import { EngineInfo } from "./EngineInfo";
import { ExposureProfile } from "./ExposureProfile";
import { FootprintD } from "./FootprintD";
import { Frameworks } from "./Frameworks";
import { Limitations } from "./Limitations";
import { ManifestM } from "./ManifestM";
import { NetworkHostsN, NetworkHostsTable } from "./NetworkHostsN";
import { PermissionsP } from "./PermissionsP";
import { ReportHeader } from "./ReportHeader";
import { SdkInventory } from "./SdkInventory";
import { CorpusHistogram } from "./charts/CorpusHistogram";
import { SdksByCategory } from "./charts/SdksByCategory";

export function ReportView({
  report,
  json,
  analysedAt,
}: {
  report: Report;
  json: string;
  analysedAt?: string | null;
}) {
  const indicators = report.indicators;
  const errors = report.errors ?? [];
  const filename = `${report.input?.sha256 ?? "report"}.json`;
  const [aboutOpen, setAboutOpen] = useState(false);
  const aboutRef = useRef<HTMLButtonElement>(null);
  const hasCategory = (report.sdk_inventory ?? []).length > 0;
  const comparison = report.comparison;
  const reason = report.comparison_reason ?? "Corpus reference unavailable";

  const chartSpan = hasCategory ? "span-4" : "span-6";
  const footprintChart = (
    <CorpusHistogram
      title="SDK footprint vs reference set"
      metricKey="D"
      metric={comparison?.metrics.D}
      valueLabel={formatPercent1(typeof comparison?.metrics.D?.value === "number" ? comparison.metrics.D.value : null)}
      comparisonReason={reason}
    />
  );
  const hostsChart = (
    <CorpusHistogram
      title="Host references vs reference set"
      metricKey="N"
      metric={comparison?.metrics.N}
      valueLabel={display(comparison?.metrics.N?.value)}
      comparisonReason={reason}
    />
  );
  const categoryChart = hasCategory ? <SdksByCategory report={report} /> : null;

  return (
    <div className="space-y-3">
      <div className="report-bento">
        <div className="span-12">
          <ReportHeader
            report={report}
            analysedAt={analysedAt}
            actions={
              <>
                <button
                  ref={aboutRef}
                  type="button"
                  className="btn-secondary inline-flex items-center gap-2"
                  aria-label="About these numbers"
                  onClick={() => setAboutOpen(true)}
                >
                  <svg viewBox="0 0 24 24" className="h-4 w-4" aria-hidden>
                    <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="2" />
                    <path d="M12 10v6M12 7h.01" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  </svg>
                  <span className="max-sm:hidden">About these numbers</span>
                </button>
                <DownloadJson json={json} filename={filename} />
              </>
            }
          />
        </div>
        <div className="span-12">
          <ExposureProfile report={report} />
        </div>
        {comparison == null ? (
          <p className="span-12" data-testid="corpus-position-reason">
            {reason}
          </p>
        ) : (
          <Tabs
            className="span-12 report-bento"
            tabs={[
              { id: "footprint", label: "Footprint", className: chartSpan, node: footprintChart },
              { id: "hosts", label: "Hosts", className: chartSpan, node: hostsChart },
              ...(categoryChart
                ? [{ id: "categories", label: "Categories", className: `${chartSpan} chart-wide`, node: categoryChart }]
                : []),
            ]}
          />
        )}
        <Tabs
          className="span-12 report-bento"
          tabs={[
            { id: "sdks", label: "SDKs", className: "table-sdk", node: <SdkInventory report={report} /> },
            { id: "host-table", label: "Hosts", className: "table-hosts", node: <NetworkHostsTable indicator={indicators?.N} /> },
          ]}
        />
      </div>

      <AboutSheet open={aboutOpen} onClose={() => setAboutOpen(false)} returnTo={aboutRef}>
        <ul>
          {(report.limitations ?? []).map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
        <p>
          {comparison
            ? `${comparison.corpus.description} Percentile compares this app with the corpus one measure at a time. It is not a risk measure.`
            : (report.comparison_reason ?? "—")}
        </p>
        {comparison?.note ? <p>{comparison.note}</p> : null}
        {report.visibility_caveat ? <p>{report.visibility_caveat}</p> : null}
      </AboutSheet>
      <Limitations report={report} />
      <p data-testid="exposure-caption">
        {comparison
          ? `${comparison.corpus.description} Percentile compares this app with the corpus one measure at a time. It is not a risk measure.`
          : (report.comparison_reason ?? "—")}
      </p>

      {report.status === "error" || errors.length > 0 ? (
        <section aria-labelledby="errors-heading" className="card">
          <h2 id="errors-heading" className="section-title">
            Errors
          </h2>
          <p>Report status: {display(report.status)}</p>
          <ul className="mt-2 list-disc pl-6">
            {errors.map((error, index) => (
              <li key={index}>
                <code>{error.code}</code>: {error.message}
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <CorpusPosition report={report} />
      <Frameworks report={report} />
      <FootprintD indicator={indicators?.D} />
      <NetworkHostsN indicator={indicators?.N} />
      <PermissionsP indicator={indicators?.P} />
      <ApisA indicator={indicators?.A} />
      <ManifestM indicator={indicators?.M} />
      <EngineInfo report={report} />
    </div>
  );
}
