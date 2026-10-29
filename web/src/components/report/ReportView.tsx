"use client";

import type { Report } from "@/lib/report-types";
import { display } from "@/lib/report-access";
import { ApisA } from "./ApisA";
import { DownloadJson } from "./DownloadJson";
import { EngineInfo } from "./EngineInfo";
import { FootprintD } from "./FootprintD";
import { Frameworks } from "./Frameworks";
import { Limitations } from "./Limitations";
import { ManifestM } from "./ManifestM";
import { NetworkHostsN } from "./NetworkHostsN";
import { PermissionsP } from "./PermissionsP";
import { ReportHeader } from "./ReportHeader";
import { SdkInventory } from "./SdkInventory";

export function ReportView({ report, json }: { report: Report; json: string }) {
  const indicators = report.indicators;
  const errors = report.errors ?? [];
  const filename = `${report.input?.sha256 ?? "report"}.json`;

  return (
    <div className="space-y-6">
      <ReportHeader report={report} />
      <Limitations report={report} />

      {report.status === "error" || errors.length > 0 ? (
        <section aria-labelledby="errors-heading" className="card">
          <h2 id="errors-heading" className="text-2xl">
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

      <Frameworks report={report} />
      <FootprintD indicator={indicators?.D} />
      <SdkInventory report={report} />
      <NetworkHostsN indicator={indicators?.N} />
      <PermissionsP indicator={indicators?.P} />
      <ApisA indicator={indicators?.A} />
      <ManifestM indicator={indicators?.M} />

      <section aria-labelledby="comparison-heading" className="card">
        <h2 id="comparison-heading" className="text-2xl">
          Comparison
        </h2>
        {report.comparison === null || report.comparison === undefined ? (
          <p>{display(report.comparison_reason)}</p>
        ) : (
          <pre className="text-sm">{JSON.stringify(report.comparison, null, 2)}</pre>
        )}
      </section>

      <EngineInfo report={report} />
      <div>
        <DownloadJson json={json} filename={filename} />
      </div>
    </div>
  );
}
