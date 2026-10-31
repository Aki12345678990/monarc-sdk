import { PACKAGE_CATEGORIES } from "@/lib/package-categories";
import type { IndicatorResult } from "@/lib/report-types";
import { asNumber, asRecord, formatPercent, rawFact } from "@/lib/report-access";
import { KeyValueTable } from "./controls";
import { IndicatorCard } from "./IndicatorCard";

// Silver data ramp; ordering only, no meaning attached.
const SEGMENT_FILLS = [
  "var(--data-1)",
  "var(--data-2)",
  "var(--data-3)",
  "var(--data-4)",
  "rgba(230,233,238,0.10)",
  "rgba(230,233,238,0.06)",
];

const OTHER_MEASURES = [
  "footprint_inclusive_pct",
  "footprint_strict_nontoolchain_pct",
  "footprint_service_pct",
  "n_packages_total",
];

export function FootprintD({ indicator }: { indicator: IndicatorResult | undefined }) {
  const details = asRecord(indicator?.details);
  const value = asNumber(indicator?.value);
  const counts = PACKAGE_CATEGORIES.map((category) => ({
    category,
    count: asNumber(details[`n_packages_${category}`]),
  }));
  const total = counts.reduce((sum, item) => sum + (item.count ?? 0), 0);

  return (
    <IndicatorCard letter="D" title="SDK footprint" indicator={indicator}>
      <p className="kpi text-3xl" data-testid="d-value">
        {formatPercent(value)}
      </p>
      {value !== null ? (
        <p className="text-sm">
          Reported value: <code>{String(value)}</code> (footprint_strict_pct)
        </p>
      ) : null}
      <h3 className="mt-4 text-xl">Package categories</h3>
      {total > 0 ? (
        <div
          role="img"
          aria-label={`Package categories: ${counts
            .map((item) => `${item.category} ${item.count ?? "—"}`)
            .join(", ")}`}
          className="mt-2 flex h-6 w-full overflow-hidden rounded border border-edge-lo"
        >
          {counts.map((item, index) =>
            item.count ? (
              <div
                key={item.category}
                style={{
                  width: `${(item.count / total) * 100}%`,
                  background: SEGMENT_FILLS[index],
                }}
              />
            ) : null,
          )}
        </div>
      ) : (
        <p>—</p>
      )}
      <ul className="mt-2 grid grid-cols-1 gap-1 text-sm sm:grid-cols-2">
        {counts.map((item, index) => (
          <li key={item.category} className="flex items-center gap-2">
            <span
              aria-hidden="true"
              className="inline-block h-3 w-3 border border-edge-lo"
              style={{ background: SEGMENT_FILLS[index] }}
            />
            <span className="font-mono">{item.category}</span>
            <span>{item.count ?? "—"}</span>
          </li>
        ))}
      </ul>

      <h3 className="mt-4 text-xl">Other footprint measures</h3>
      <KeyValueTable
        caption="Other footprint measures"
        rows={[
          ...OTHER_MEASURES.map((key): [string, string] => [key, rawFact(details[key])]),
          ["n_sdk_distinct", rawFact(details.n_sdk_distinct)],
        ]}
      />
    </IndicatorCard>
  );
}
