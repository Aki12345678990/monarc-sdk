import { PACKAGE_CATEGORIES } from "@/lib/package-categories";
import type { IndicatorResult } from "@/lib/report-types";
import { asNumber, asRecord, asString, formatPercent, rawFact } from "@/lib/report-access";
import { KeyValueTable } from "./controls";
import { IndicatorCard } from "./IndicatorCard";

// Neutral shades of charcoal on cream; ordering only, no meaning attached.
const SEGMENT_CLASSES = [
  "bg-charcoal",
  "bg-charcoal/80",
  "bg-charcoal/60",
  "bg-charcoal/40",
  "bg-charcoal/20",
  "bg-cream",
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
  const note = asString(details.note);
  const counts = PACKAGE_CATEGORIES.map((category) => ({
    category,
    count: asNumber(details[`n_packages_${category}`]),
  }));
  const total = counts.reduce((sum, item) => sum + (item.count ?? 0), 0);

  return (
    <IndicatorCard letter="D" title="SDK footprint" indicator={indicator}>
      <p className="text-3xl font-semibold" data-testid="d-value">
        {formatPercent(value)}
      </p>
      {value !== null ? (
        <p className="text-sm">
          Reported value: <code>{String(value)}</code> (footprint_strict_pct)
        </p>
      ) : null}
      {note ? <p className="mt-1">Note: {note}</p> : null}

      <h3 className="mt-4 text-xl">Package categories</h3>
      {total > 0 ? (
        <div
          role="img"
          aria-label={`Package categories: ${counts
            .map((item) => `${item.category} ${item.count ?? "—"}`)
            .join(", ")}`}
          className="mt-2 flex h-6 w-full overflow-hidden rounded border border-charcoal"
        >
          {counts.map((item, index) =>
            item.count ? (
              <div
                key={item.category}
                className={SEGMENT_CLASSES[index]}
                style={{ width: `${(item.count / total) * 100}%` }}
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
              className={`inline-block h-3 w-3 border border-charcoal ${SEGMENT_CLASSES[index]}`}
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
