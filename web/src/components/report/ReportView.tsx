"use client";

import { FadeUp, Stagger } from "@/components/motion/Stagger";
import { Reveal } from "@/components/motion/Reveal";
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
      <Stagger className="space-y-6">
        <FadeUp>
          <ReportHeader report={report} />
        </FadeUp>
        <FadeUp>
          <Limitations report={report} />
        </FadeUp>
        <FadeUp>
          <ExposureProfile report={report} />
        </FadeUp>
      </Stagger>

      <Reveal>
        <PackageComposition indicator={indicators?.D} />
      </Reveal>
      <Reveal>
        <SdksByCategory report={report} />
      </Reveal>
      <Reveal>
        <HostsByAttribution indicator={indicators?.N} />
      </Reveal>
      <Reveal>
        <CorpusPosition report={report} />
      </Reveal>
      <Reveal>
        <TopSdks report={report} />
      </Reveal>

      {report.status === "error" || errors.length > 0 ? (
        <Reveal>
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
        </Reveal>
      ) : null}

      <Reveal>
        <Frameworks report={report} />
      </Reveal>
      <Reveal>
        <FootprintD indicator={indicators?.D} />
      </Reveal>
      <Reveal>
        <SdkInventory report={report} />
      </Reveal>
      <Reveal>
        <NetworkHostsN indicator={indicators?.N} />
      </Reveal>
      <Reveal>
        <PermissionsP indicator={indicators?.P} />
      </Reveal>
      <Reveal>
        <ApisA indicator={indicators?.A} />
      </Reveal>
      <Reveal>
        <ManifestM indicator={indicators?.M} />
      </Reveal>
      <Reveal>
        <EngineInfo report={report} />
      </Reveal>
      <Reveal>
        <div>
          <DownloadJson json={json} filename={filename} />
        </div>
      </Reveal>
    </div>
  );
}
