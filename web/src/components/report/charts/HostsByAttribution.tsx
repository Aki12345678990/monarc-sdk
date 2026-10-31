"use client";

import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { RECHARTS_DURATION_MS, RECHARTS_EASING } from "@/lib/motion";
import { asArray, asRecord, asString } from "@/lib/report-access";
import type { IndicatorResult } from "@/lib/report-types";
import { BarSilverDefs, ChartFrame, HiddenTable, useBarSilverId } from "./ChartFrame";

const GROUPS = ["sdk", "first_party", "other"] as const;

export function HostsByAttribution({ indicator }: { indicator: IndicatorResult | undefined }) {
  const silverId = useBarSilverId();
  const hosts = asArray(asRecord(indicator?.details).hosts).map(asRecord);
  const buckets = { sdk: new Set<string>(), first_party: new Set<string>(), other: new Set<string>() };
  for (const row of hosts) {
    const host = asString(row.host);
    if (!host) continue;
    const attribution = asString(row.attribution);
    if (attribution === "sdk") buckets.sdk.add(host);
    else if (attribution === "first_party") buckets.first_party.add(host);
    else buckets.other.add(host);
  }
  const rows = GROUPS.map((group) => ({
    group,
    count: buckets[group].size,
  }));
  const empty = hosts.length === 0;

  return (
    <ChartFrame
      title="Network hosts by attribution"
      caption="Distinct hosts in this report's hosts list, grouped by attribution. Other is every attribution that is not sdk or first_party."
      empty={empty}
      table={
        <HiddenTable
          caption="Network hosts by attribution"
          columns={["attribution", "distinct hosts"]}
          rows={rows.map((row) => [row.group, row.count])}
        />
      }
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows}>
          <BarSilverDefs id={silverId} />
          <XAxis dataKey="group" />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Bar
            dataKey="count"
            isAnimationActive
            animationDuration={RECHARTS_DURATION_MS}
            animationEasing={RECHARTS_EASING}
            name="distinct hosts"
            fill={`url(#${silverId})`}
          >
            {rows.map((row) => (
              <Cell key={row.group} fill={`url(#${silverId})`} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}
