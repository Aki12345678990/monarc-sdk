"use client";

import { Bar, BarChart, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { CHART_PALETTE } from "@/lib/chart-palette";
import { RECHARTS_DURATION_MS, RECHARTS_EASING } from "@/lib/motion";
import { asArray, asRecord, asString } from "@/lib/report-access";
import type { Report } from "@/lib/report-types";
import { ChartFrame, HiddenTable } from "./ChartFrame";

export function SdksByCategory({ report }: { report: Report }) {
  const counts = new Map<string, { sdks: number; packages: number }>();
  for (const entry of asArray(report.sdk_inventory).map(asRecord)) {
    const category = asString(entry.sdk_category) ?? "—";
    const current = counts.get(category) ?? { sdks: 0, packages: 0 };
    current.sdks += 1;
    current.packages += asArray(entry.packages).length;
    counts.set(category, current);
  }
  const rows = [...counts.entries()]
    .map(([category, value]) => ({ category, ...value }))
    .sort((a, b) => b.sdks - a.sdks || a.category.localeCompare(b.category));

  return (
    <ChartFrame
      title="SDKs by category"
      caption="Number of distinct SDKs in this app's inventory, grouped by sdk_category. The label is the package count."
      empty={rows.length === 0}
      table={
        <HiddenTable
          caption="SDKs by category"
          columns={["sdk_category", "distinct SDKs", "packages"]}
          rows={rows.map((row) => [row.category, row.sdks, row.packages])}
        />
      }
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows} layout="vertical" margin={{ left: 8, right: 16 }}>
          <XAxis type="number" allowDecimals={false} />
          <YAxis type="category" dataKey="category" width={120} />
          <Tooltip />
          <Bar
            dataKey="sdks"
            isAnimationActive
            animationDuration={RECHARTS_DURATION_MS}
            animationEasing={RECHARTS_EASING}
            animationBegin={0}
            name="distinct SDKs"
          >
            {rows.map((row, index) => (
              <Cell key={row.category} fill={CHART_PALETTE[index % CHART_PALETTE.length]} />
            ))}
            <LabelList dataKey="packages" position="right" />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}
