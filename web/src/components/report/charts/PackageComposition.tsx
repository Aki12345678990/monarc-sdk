"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { CHART_PALETTE } from "@/lib/chart-palette";
import { RECHARTS_DURATION_MS, RECHARTS_EASING } from "@/lib/motion";
import { PACKAGE_CATEGORIES } from "@/lib/package-categories";
import { asNumber, asRecord } from "@/lib/report-access";
import type { IndicatorResult } from "@/lib/report-types";
import { ChartFrame, HiddenTable } from "./ChartFrame";

export function PackageComposition({ indicator }: { indicator: IndicatorResult | undefined }) {
  const details = asRecord(indicator?.details);
  const rows = PACKAGE_CATEGORIES.map((category, index) => {
    const count = asNumber(details[`n_packages_${category}`]) ?? 0;
    return { category, count, fill: CHART_PALETTE[index] };
  }).filter((row) => row.count > 0);
  const total = rows.reduce((sum, row) => sum + row.count, 0);

  return (
    <ChartFrame
      title="Package composition"
      caption="Share of this app's packages by namespace category. Counts, not code volume."
      empty={total === 0}
      table={
        <HiddenTable
          caption="Package composition"
          columns={["category", "count", "percent"]}
          rows={rows.map((row) => [
            row.category,
            row.count,
            total ? `${((row.count / total) * 100).toFixed(1)}%` : "—",
          ])}
        />
      }
    >
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={rows}
            dataKey="count"
            nameKey="category"
            cx="50%"
            cy="50%"
            innerRadius={48}
            outerRadius={80}
            isAnimationActive
            animationDuration={RECHARTS_DURATION_MS}
            animationEasing={RECHARTS_EASING}
          >
            {rows.map((row) => (
              <Cell key={row.category} fill={row.fill} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: "var(--bg-2)",
              border: "1px solid var(--edge-hi)",
              borderRadius: 12,
              color: "var(--text)",
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}
