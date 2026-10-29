import { asArray, asRecord, asString, display, formatPercent1, formatPercentile } from "@/lib/report-access";
import { INDICATOR_STATUS_LABELS } from "@/lib/labels";
import type { Report } from "@/lib/report-types";

function Tile({
  label,
  value,
  extra,
  testId,
}: {
  label: string;
  value: string;
  extra?: string | null;
  testId: string;
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
    </div>
  );
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

  return (
    <section aria-labelledby="exposure-heading" className="space-y-3">
      <h2 id="exposure-heading" className="text-2xl">
        Exposure profile
      </h2>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <Tile
          label="SDK footprint"
          value={formatPercent1(dValue)}
          extra={formatPercentile(comparison?.metrics.D?.percentile)}
          testId="tile-d"
        />
        <Tile
          label="Distinct SDKs"
          value={display(sdkValue)}
          extra={formatPercentile(comparison?.metrics.n_sdk_distinct?.percentile)}
          testId="tile-sdks"
        />
        <Tile
          label="Distinct network hosts"
          value={display(nValue)}
          extra={formatPercentile(comparison?.metrics.N?.percentile)}
          testId="tile-n"
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
