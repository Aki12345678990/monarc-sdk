import { EXPOSURE_DISCLAIMER } from "@/lib/exposure-copy";
import { asRecord } from "@/lib/report-access";
import type { Report } from "@/lib/report-types";

function times100(value: number | null | undefined): string | null {
  if (typeof value !== "number" || Number.isNaN(value)) return null;
  return (value * 100).toFixed(1);
}

export function ExposureIndex({ report }: { report: Report }) {
  const composite = report.composite;
  const r = times100(composite?.R);
  const withoutD = times100(composite?.R_minusD);
  const size = times100(composite?.size_percentile);
  const reason = composite?.reason ?? (composite ? null : "Exposure index unavailable");
  const percentiles = asRecord(composite?.percentiles);

  return (
    <section aria-labelledby="exposure-index-heading" className="card" data-testid="exposure-index">
      <h2 id="exposure-index-heading" className="section-title">
        Exposure index R
      </h2>
      {r == null ? (
        <p data-testid="exposure-index-reason">{reason}</p>
      ) : (
        <p className="kpi" data-testid="exposure-index-r">
          {r}
        </p>
      )}
      <p className="mt-2 text-sm">
        R₋D (tested in the paper)
        {withoutD == null ? null : (
          <span className="ml-2 font-semibold" data-testid="exposure-index-rmd">
            {withoutD}
          </span>
        )}
      </p>
      <p className="text-sm text-muted">
        R₋D leaves out D because the paper tests D against it; including D would correlate D with itself.
      </p>
      <p className="mt-2 text-sm" data-testid="exposure-index-formula">
        R = ¼·pr(P) + ¼·pr(A) + ¼·pr(N) + ¼·pr(D)
        <span className="mx-2">·</span>
        R₋D = ⅓·pr(P) + ⅓·pr(A) + ⅓·pr(N)
      </p>
      <p className="text-sm text-muted">pr = percentile rank against the 1,260-app research corpus</p>
      {size != null ? (
        <p className="mt-2 text-sm" data-testid="exposure-index-size">
          App size: higher than {size}% of corpus apps
        </p>
      ) : null}
      <p className="mt-2 text-sm" data-testid="exposure-index-disclaimer">
        {EXPOSURE_DISCLAIMER}
      </p>
      {r != null ? (
        <p className="sr-only">
          {Object.entries(percentiles)
            .map(([name, value]) => `${name} ${typeof value === "number" ? (value * 100).toFixed(1) : "—"}`)
            .join(", ")}
        </p>
      ) : null}
    </section>
  );
}
