"use client";

import type { Report } from "@/lib/report-types";
import { display } from "@/lib/report-access";
import { ApisA } from "./ApisA";
import { CorpusPosition } from "./CorpusPosition";
import { DownloadJson } from "./DownloadJson";
import { EngineInfo } from "./EngineInfo";
import { ExposureProfile } from "./ExposureProfile";
import { FootprintD } from "./FootprintD";
import { Frameworks } from "./Frameworks";
import { Limitations } from "./Limitations";
import { ManifestM } from "./ManifestM";
import { NetworkHostsN } from "./NetworkHostsN";
import { PermissionsP } from "./PermissionsP";
import { ReportHeader } from "./ReportHeader";
import { SdkInventory } from "./SdkInventory";
import { HostsByAttribution } from "./charts/HostsByAttribution";
import { PackageComposition } from "./charts/PackageComposition";
import { SdksByCategory } from "./charts/SdksByCategory";
import { TopSdks } from "./charts/TopSdks";

export function ReportView({ report, json }: { report: Report; json: string }) {
  const indicators = report.indicators;
  const errors = report.errors ?? [];
  const filename = `${report.input?.sha256 ?? "report"}.json`;

  return (
    <div className="space-y-6">
      <ReportHeader report={report} />
      <Limitations report={report} />
      <ExposureProfile report={report} />
      <PackageComposition indicator={indicators?.D} />
      <SdksByCategory report={report} />
      <HostsByAttribution indicator={indicators?.N} />
      <CorpusPosition report={report} />
      <TopSdks report={report} />

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

      <EngineInfo report={report} />
      <div>
        <DownloadJson json={json} filename={filename} />
      </div>
    </div>
  );
}
