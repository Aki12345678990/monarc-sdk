import { display } from "@/lib/report-access";
import type { Report } from "@/lib/report-types";
import { CorpusHistogram } from "./charts/CorpusHistogram";

export function CorpusPosition({ report }: { report: Report }) {
  const comparison = report.comparison;
  const sdks = comparison?.metrics.n_sdk_distinct;
  if (comparison == null) return null;

  return (
    <CorpusHistogram
      title="Distinct SDKs"
      metric={sdks}
      valueLabel={display(sdks?.value)}
    />
  );
}
