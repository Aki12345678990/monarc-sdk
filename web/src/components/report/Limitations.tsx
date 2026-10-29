import type { Report } from "@/lib/report-types";

export function Limitations({ report }: { report: Report }) {
  const items = report.limitations ?? [];
  return (
    <section aria-labelledby="limitations-heading" className="card border-2 border-charcoal">
      <h2 id="limitations-heading" className="text-2xl">
        Limitations
      </h2>
      {items.length === 0 ? (
        <p>—</p>
      ) : (
        <ul className="mt-2 list-disc pl-6" data-testid="limitations">
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      )}
    </section>
  );
}
