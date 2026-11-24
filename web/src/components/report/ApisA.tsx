import type { IndicatorResult } from "@/lib/report-types";
import { asArray, asRecord, display } from "@/lib/report-access";
import { IndicatorCard } from "./IndicatorCard";

export function ApisA({ indicator }: { indicator: IndicatorResult | undefined }) {
  const pairs = asArray(asRecord(indicator?.details).pairs).map(asRecord);
  return (
    <IndicatorCard letter="A" title="Sensitive APIs" indicator={indicator}>
      <h3 className="text-xl">Mapped pairs called from SDK code</h3>
      {pairs.length === 0 ? (
        <p>—</p>
      ) : (
        <table className="data-table mt-2">
          <caption className="sr-only">Sensitive API pairs</caption>
          <thead>
            <tr>
              <th scope="col">API</th>
              <th scope="col">Required permission</th>
              <th scope="col">SDK</th>
            </tr>
          </thead>
          <tbody>
            {pairs.map((pair, index) => {
              const callers = asArray(pair.callers)
                .map(asRecord)
                .map((caller) => `${display(caller.sdk_name)} (${display(caller.n_callsites)})`)
                .join(", ");
              return (
                <tr key={index}>
                  <td className="font-mono text-sm break-all">
                    {display(pair.class)}.{display(pair.method)}
                  </td>
                  <td className="font-mono text-sm">{display(pair.permission)}</td>
                  <td className="text-sm">{callers || "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </IndicatorCard>
  );
}
