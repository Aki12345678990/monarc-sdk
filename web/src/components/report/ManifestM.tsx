"use client";

import { useState } from "react";
import type { IndicatorResult } from "@/lib/report-types";
import { asArray, asRecord, display, matchesFilter, rawFact } from "@/lib/report-access";
import { FilterInput, KeyValueTable, PAGE_SIZE, ShowMore } from "./controls";
import { IndicatorCard } from "./IndicatorCard";

const COMPONENT_COLUMNS = [
  "type",
  "name",
  "exported_explicit",
  "has_intent_filter",
  "permission",
  "is_launcher",
] as const;

export function ManifestM({ indicator }: { indicator: IndicatorResult | undefined }) {
  const [filter, setFilter] = useState("");
  const [shown, setShown] = useState(PAGE_SIZE);
  const details = asRecord(indicator?.details);
  const factKeys = Object.keys(details).filter((key) => key !== "components");
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
      <h3 className="text-xl">Raw manifest facts</h3>
      {factKeys.length === 0 ? (
        <p>—</p>
      ) : (
        <KeyValueTable
          caption="Raw manifest facts"
          rows={factKeys.map((key): [string, string] => [key, rawFact(details[key])])}
        />
      )}

      <h3 className="mt-4 text-xl">Components</h3>
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
