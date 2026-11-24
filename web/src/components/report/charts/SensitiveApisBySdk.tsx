"use client";

import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { asArray, asRecord, asString } from "@/lib/report-access";
import type { IndicatorResult } from "@/lib/report-types";
import { BarSilverDefs, ChartFrame, HiddenTable, useBarSilverId } from "./ChartFrame";

export function SensitiveApisBySdk({ indicator }: { indicator: IndicatorResult | undefined }) {
  const silverId = useBarSilverId();
  const pairs = asArray(asRecord(indicator?.details).pairs).map(asRecord);
  const counts = new Map<string, Set<string>>();
  for (const pair of pairs) {
    const key = `${asString(pair.class) ?? ""}#${asString(pair.method) ?? ""}`;
    for (const caller of asArray(pair.callers).map(asRecord)) {
      const name = asString(caller.sdk_name) || "—";
      const bucket = counts.get(name) ?? new Set<string>();
      bucket.add(key);
      counts.set(name, bucket);
    }
  }
  const rows = [...counts.entries()]
    .map(([name, set]) => ({ name, pairs: set.size }))
    .sort((a, b) => b.pairs - a.pairs || a.name.localeCompare(b.name))
    .slice(0, 8);

  return (
    <ChartFrame
      title="Sensitive APIs by SDK"
      caption="Distinct mapped class and method pairs, by the SDK that calls them."
      empty={rows.length === 0}
      table={
        <HiddenTable
          caption="Sensitive APIs by SDK"
          columns={["sdk", "pairs"]}
          rows={rows.map((row) => [row.name, row.pairs])}
        />
      }
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows} layout="vertical" margin={{ left: 8, right: 16 }}>
          <BarSilverDefs id={silverId} />
          <XAxis type="number" allowDecimals={false} />
          <YAxis type="category" dataKey="name" width={140} />
          <Tooltip />
          <Bar dataKey="pairs" isAnimationActive={false}>
            {rows.map((row) => (
              <Cell key={row.name} fill={`url(#${silverId})`} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}
