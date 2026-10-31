"use client";

import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { RECHARTS_DURATION_MS, RECHARTS_EASING } from "@/lib/motion";
import { asArray, asRecord, asString } from "@/lib/report-access";
import type { Report } from "@/lib/report-types";
import { BarSilverDefs, ChartFrame, HiddenTable, useBarSilverId } from "./ChartFrame";

export function TopSdks({ report }: { report: Report }) {
  const silverId = useBarSilverId();
  const rows = asArray(report.sdk_inventory)
    .map(asRecord)
    .map((entry) => ({
      name: asString(entry.sdk_name) ?? "—",
      packages: asArray(entry.packages).length,
    }))
    .sort((a, b) => b.packages - a.packages || a.name.localeCompare(b.name))
    .slice(0, 10);

  return (
    <ChartFrame
      title="Top SDKs by package count"
      caption="The ten SDKs in this app's inventory with the most attributed packages."
      empty={rows.length === 0}
      table={
        <HiddenTable
          caption="Top SDKs by package count"
          columns={["sdk_name", "packages"]}
          rows={rows.map((row) => [row.name, row.packages])}
        />
      }
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows} layout="vertical" margin={{ left: 8, right: 16 }}>
          <BarSilverDefs id={silverId} />
          <XAxis type="number" allowDecimals={false} />
          <YAxis type="category" dataKey="name" width={140} />
          <Tooltip />
          <Bar
            dataKey="packages"
            isAnimationActive
            animationDuration={RECHARTS_DURATION_MS}
            animationEasing={RECHARTS_EASING}
            name="packages"
            fill={`url(#${silverId})`}
          >
            {rows.map((row) => (
              <Cell key={row.name} fill={`url(#${silverId})`} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}
