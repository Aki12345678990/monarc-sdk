"use client";

import { Bar, BarChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { asRecord } from "@/lib/report-access";
import type { Report } from "@/lib/report-types";
import { BarSilverDefs, ChartFrame, HiddenTable, useBarSilverId } from "./ChartFrame";

const ORDER = ["P", "A", "N", "D"] as const;

export function IndicatorPercentiles({ report }: { report: Report }) {
  const silverId = useBarSilverId();
  const percentiles = asRecord(report.composite?.percentiles);
  const rows = ORDER.map((name) => {
    const raw = percentiles[name];
    const value = typeof raw === "number" ? raw * 100 : 0;
    return { name, value };
  });
  const mark = typeof report.composite?.R === "number" ? report.composite.R * 100 : null;
  const empty = report.composite?.R == null;

  return (
    <ChartFrame
      title="Indicator percentiles"
      caption="Each bar is that indicator's percentile rank. The line marks R."
      empty={empty}
      table={
        <HiddenTable
          caption="Indicator percentiles"
          columns={["indicator", "percentile"]}
          rows={rows.map((row) => [row.name, row.value.toFixed(1)])}
        />
      }
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows} layout="vertical" margin={{ left: 8, right: 16 }}>
          <BarSilverDefs id={silverId} />
          <XAxis type="number" domain={[0, 100]} />
          <YAxis type="category" dataKey="name" width={36} />
          <Tooltip />
          {mark != null ? <ReferenceLine x={mark} stroke="var(--data-1)" /> : null}
          <Bar dataKey="value" fill={`url(#${silverId})`} isAnimationActive={false} />
        </BarChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}
