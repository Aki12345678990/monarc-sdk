import type { IndicatorResult } from "@/lib/report-types";
import { asArray, asRecord, display } from "@/lib/report-access";
import { IndicatorCard } from "./IndicatorCard";

export function PermissionsP({ indicator }: { indicator: IndicatorResult | undefined }) {
  const permissions = asArray(asRecord(indicator?.details).permissions).map(asRecord);
  return (
    <IndicatorCard letter="P" title="Dangerous permissions" indicator={indicator}>
      <h3 className="text-xl">Counted dangerous permissions</h3>
      {permissions.length === 0 ? (
        <p>—</p>
      ) : (
        <table className="data-table mt-2">
          <caption className="sr-only">Counted dangerous permissions</caption>
          <thead>
            <tr>
              <th scope="col">Permission</th>
              <th scope="col">Declaring tag</th>
            </tr>
          </thead>
          <tbody>
            {permissions.map((permission, index) => (
              <tr key={index}>
                <td className="font-mono text-sm break-all">{display(permission.name)}</td>
                <td className="font-mono text-sm">{asArray(permission.tags).map(display).join(", ")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </IndicatorCard>
  );
}
