import { display, formatPercent1 } from "@/lib/report-access";
import type { Report } from "@/lib/report-types";
import { CorpusHistogram } from "./charts/CorpusHistogram";

export function CorpusPosition({ report }: { report: Report }) {
  const comparison = report.comparison;
  const d = comparison?.metrics.D;
  const n = comparison?.metrics.N;
  const sdks = comparison?.metrics.n_sdk_distinct;
  const reason = report.comparison_reason ?? "Corpus reference unavailable";

  return (
    <section aria-labelledby="corpus-heading" className="space-y-3">
      <h2 id="corpus-heading" className="text-2xl">
        Corpus position
      </h2>
      {comparison == null ? (
        <p data-testid="corpus-position-reason">{reason}</p>
      ) : (
        <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
          <CorpusHistogram
            title="D"
            metric={d}
            valueLabel={formatPercent1(typeof d?.value === "number" ? d.value : null)}
            comparisonReason={reason}
          />
          <CorpusHistogram
            title="N"
            metric={n}
            valueLabel={display(n?.value)}
            comparisonReason={reason}
          />
          <CorpusHistogram
            title="Distinct SDKs"
            metric={sdks}
            valueLabel={display(sdks?.value)}
            comparisonReason={reason}
          />
        </div>
      )}
    </section>
  );
}
