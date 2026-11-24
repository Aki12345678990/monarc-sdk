"use client";

import { useState } from "react";
import type { IndicatorResult } from "@/lib/report-types";
import { asArray, asRecord, display, matchesFilter, rawFact } from "@/lib/report-access";
import { FilterInput, PAGE_SIZE, ShowMore } from "./controls";
import { IndicatorCard } from "./IndicatorCard";

const COMPONENT_COLUMNS = ["name", "type", "sdk_name", "protection"] as const;

export function ManifestM({ indicator }: { indicator: IndicatorResult | undefined }) {
  const [filter, setFilter] = useState("");
  const [shown, setShown] = useState(PAGE_SIZE);
  const details = asRecord(indicator?.details);
  const components = asArray(details.components).map(asRecord);
  const filtered = components.filter((component) =>
    matchesFilter(filter, ...COMPONENT_COLUMNS.map((column) => component[column])),
  );

  function onFilter(value: string) {
    setFilter(value);
    setShown(PAGE_SIZE);
  }

  return (
    <IndicatorCard letter="M" title="Manifest facts" indicator={indicator}>
      <h3 className="text-xl">Flags, listed separately</h3>
      <p className="text-sm">
        debuggable {display(details.F_debug)} · allowBackup {display(details.F_backup)} · cleartext{" "}
        {display(details.F_cleartext)}
      </p>
      <p className="text-sm text-muted">
        M_exp {display(details.M_exp)} · M_exp_sdk {display(details.M_exp_sdk)}
      </p>
      <h3 className="mt-3 text-xl">Counted exported components</h3>
      <FilterInput label="Filter components" value={filter} onChange={onFilter} />
      <div className="overflow-x-auto">
        <table className="data-table">
          <caption className="sr-only">Manifest components</caption>
          <thead>
            <tr>
              {COMPONENT_COLUMNS.map((column) => (
                <th key={column} scope="col" className="font-mono text-sm">
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={COMPONENT_COLUMNS.length}>—</td>
              </tr>
            ) : (
              filtered.slice(0, shown).map((component, index) => (
                <tr key={`${display(component.type)}-${display(component.name)}-${index}`}>
                  {COMPONENT_COLUMNS.map((column) => (
                    <td key={column} className="font-mono text-sm break-all">
                      {rawFact(component[column])}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <ShowMore
        shown={shown}
        total={filtered.length}
        noun="components"
        onMore={() => setShown((value) => value + PAGE_SIZE)}
      />
    </IndicatorCard>
  );
}
