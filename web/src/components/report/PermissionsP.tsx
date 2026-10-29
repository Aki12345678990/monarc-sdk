import type { IndicatorResult } from "@/lib/report-types";
import { asArray, asRecord, display } from "@/lib/report-access";
import { IndicatorCard } from "./IndicatorCard";

export function PermissionsP({ indicator }: { indicator: IndicatorResult | undefined }) {
  const permissions = asArray(asRecord(indicator?.details).permissions_requested);
  return (
    <IndicatorCard letter="P" title="Permissions" indicator={indicator}>
      <h3 className="text-xl">Requested permissions (raw, unclassified)</h3>
      {permissions.length === 0 ? (
        <p>—</p>
      ) : (
        <ul className="mt-2 list-disc pl-6 font-mono text-sm">
          {permissions.map((permission, index) => (
            <li key={index} className="break-all">
              {display(permission)}
            </li>
          ))}
        </ul>
      )}
    </IndicatorCard>
  );
}
