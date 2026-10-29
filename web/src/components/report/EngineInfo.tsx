import type { Report } from "@/lib/report-types";
import { display } from "@/lib/report-access";
import { KeyValueTable } from "./controls";

export function EngineInfo({ report }: { report: Report }) {
  const engine = report.engine;
  return (
    <section aria-labelledby="engine-heading" className="card">
      <h2 id="engine-heading" className="text-2xl">
        Engine
      </h2>
      <KeyValueTable
        caption="Engine"
        rows={[
          ["analyzer_core version", display(engine?.version)],
          ["androguard version", display(engine?.androguard_version)],
          ["reference status", display(engine?.reference_status)],
          ["schema_version", display(report.schema_version)],
          ["corpus", display(report.comparison?.corpus.name)],
          ["corpus reference hash", display(report.comparison?.corpus.reference_sha256)],
        ]}
      />
    </section>
  );
}
