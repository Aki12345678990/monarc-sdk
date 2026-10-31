"use client";

import { useState } from "react";
import type { IndicatorResult } from "@/lib/report-types";
import { asArray, asRecord, display, matchesFilter, rawFact } from "@/lib/report-access";
import { FilterInput, KeyValueTable } from "./controls";
import { IndicatorCard } from "./IndicatorCard";

export function NetworkHostsTable({ indicator }: { indicator: IndicatorResult | undefined }) {
  const [filter, setFilter] = useState("");
  const details = asRecord(indicator?.details);
  const hosts = asArray(details.hosts).map(asRecord);
  const filtered = hosts.filter((host) =>
    matchesFilter(filter, host.host, host.attribution, host.sdk_name),
  );

  return (
    <section aria-labelledby="hosts-table-heading" className="card table-panel table-hosts">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 id="hosts-table-heading" className="section-title">
          Network host references
        </h2>
        <p className="text-sm">{filtered.length} / {hosts.length}</p>
      </div>
      <FilterInput label="Filter hosts" value={filter} onChange={setFilter} />
      <div className="table-scroll">
        <table className="data-table">
          <caption className="sr-only">Network hosts</caption>
          <thead>
            <tr>
              <th scope="col">Host</th>
              <th scope="col">Attribution</th>
              <th scope="col">SDK name</th>
              <th scope="col">IP literal</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={4}>—</td>
              </tr>
            ) : (
              filtered.map((host, index) => (
                <tr key={`${display(host.host)}-${display(host.caller_package)}-${index}`}>
                  <td className="font-mono text-sm break-all">{display(host.host)}</td>
                  <td>{display(host.attribution)}</td>
                  <td>{display(host.sdk_name)}</td>
                  <td>{rawFact(host.ip_literal)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export function NetworkHostsN({ indicator }: { indicator: IndicatorResult | undefined }) {
  const details = asRecord(indicator?.details);
  return (
    <IndicatorCard letter="N" title="Network hosts" indicator={indicator}>
      <p className="kpi" data-testid="n-value">
        {display(indicator?.value)}
      </p>
      <p className="text-sm">Distinct hosts (hosts_distinct_all)</p>
      <KeyValueTable
        caption="Host counts"
        rows={[
          ["hosts_distinct_sdk", rawFact(details.hosts_distinct_sdk)],
          ["hosts_distinct_first_party", rawFact(details.hosts_distinct_first_party)],
          ["n_urls_unparseable", rawFact(details.n_urls_unparseable)],
        ]}
      />
    </IndicatorCard>
  );
}
