import type { IndicatorResult } from "@/lib/report-types";
import { asRecord, rawFact } from "@/lib/report-access";
import { KeyValueTable } from "./controls";
import { IndicatorCard } from "./IndicatorCard";

export function ApisA({ indicator }: { indicator: IndicatorResult | undefined }) {
  const details = asRecord(indicator?.details);
  const keys = Object.keys(details);
  return (
    <IndicatorCard letter="A" title="Sensitive APIs" indicator={indicator}>
      {keys.length > 0 ? (
        <>
          <h3 className="text-xl">Recorded facts (raw)</h3>
          <KeyValueTable
            caption="A recorded facts"
            rows={keys.map((key): [string, string] => [key, rawFact(details[key])])}
          />
        </>
      ) : null}
    </IndicatorCard>
  );
}
