import type { Report } from "@/lib/report-types";
import { asArray, asRecord, display } from "@/lib/report-access";

export function Frameworks({ report }: { report: Report }) {
  const frameworks = asArray(report.frameworks).map(asRecord);
  return (
    <section aria-labelledby="frameworks-heading" className="card">
      <h2 id="frameworks-heading" className="text-2xl">
        Frameworks
      </h2>
      {frameworks.length === 0 ? (
        <p className="mt-2">No cross-platform framework detected.</p>
      ) : (
        <ul className="mt-2 space-y-2">
          {frameworks.map((framework, index) => (
            <li key={`${display(framework.name)}-${index}`}>
              <span className="font-semibold">{display(framework.name)}</span>
              {asArray(framework.evidence).length > 0 ? (
                <>
                  <span> — evidence:</span>
                  <ul className="list-disc pl-6 font-mono text-sm">
                    {asArray(framework.evidence).map((item, i) => (
                      <li key={i} className="break-all">
                        {display(item)}
                      </li>
                    ))}
                  </ul>
                </>
              ) : null}
            </li>
          ))}
        </ul>
      )}
      {report.visibility_caveat ? (
        <p className="mt-3 border-l-4 border-edge-hi pl-3">
          <span className="font-semibold">Visibility caveat: </span>
          {report.visibility_caveat}
        </p>
      ) : null}
    </section>
  );
}
