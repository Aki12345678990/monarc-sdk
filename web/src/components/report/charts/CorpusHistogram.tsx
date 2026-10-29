"use client";

import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { CHART_CHARCOAL, CHART_ORANGE } from "@/lib/chart-palette";
import { formatPercentile } from "@/lib/report-access";
import type { MetricComparison } from "@/lib/report-types";
import { ChartFrame, HiddenTable } from "./ChartFrame";

export type CorpusHistogramProps = {
  title: string;
  /** A single univariate corpus metric. Never pass a second metric. */
  metric: MetricComparison | null | undefined;
  valueLabel: string;
  comparisonReason?: string | null;
};

export function CorpusHistogram({ title, metric, valueLabel, comparisonReason }: CorpusHistogramProps) {
  const counts = metric?.histogram.counts ?? [];
  const appBin = metric?.histogram.app_bin;
  const rows = counts.map((count, index) => ({
    bin: index,
    count,
    highlight: appBin === index,
  }));
  const highlighted = rows.filter((row) => row.highlight);
  const percentileText = formatPercentile(metric?.percentile ?? null);
  const empty = metric == null || counts.length === 0;

  if (metric == null && comparisonReason) {
    return (
      <section className="card">
        <h3 className="text-xl">{title}</h3>
        <p className="mt-2" data-testid={`corpus-reason-${title}`}>
          {comparisonReason}
        </p>
      </section>
    );
  }

  return (
    <ChartFrame
      title={title}
      caption={`Corpus histogram for this one measure. This app: ${valueLabel}${
        percentileText ? ` (${percentileText})` : ""
      }.`}
      empty={empty}
      table={
        <HiddenTable
          caption={`${title} corpus histogram`}
          columns={["bin", "count", "this app"]}
          rows={rows.map((row) => [row.bin, row.count, row.highlight ? "yes" : "no"])}
        />
      }
      legend={
        <>
          <p className="mt-2 text-sm" data-testid={`corpus-label-${title}`}>
            This app: {valueLabel}
            {percentileText ? ` (${percentileText})` : ""}
          </p>
          <p className="sr-only" data-testid={`histogram-highlight-count-${title}`}>
            {highlighted.length}
          </p>
        </>
      }
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows}>
          <XAxis dataKey="bin" />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Bar dataKey="count" isAnimationActive={false} name="corpus apps">
            {rows.map((row) => (
              <Cell
                key={row.bin}
                fill={row.highlight ? CHART_ORANGE : CHART_CHARCOAL}
                data-testid={`histogram-bin-${row.bin}`}
                data-app-bin={row.highlight ? "true" : "false"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}
