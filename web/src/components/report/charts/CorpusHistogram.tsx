"use client";

import { motion } from "motion/react";
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { CHART_ACCENT } from "@/lib/chart-palette";
import { DURATION, EASE, STAGGER } from "@/lib/motion";
import { formatPercentile } from "@/lib/report-access";
import type { MetricComparison } from "@/lib/report-types";
import { BarSilverDefs, ChartFrame, HiddenTable, useBarSilverId } from "./ChartFrame";

export type CorpusHistogramProps = {
  title: string;
  /** A single univariate corpus metric. Never pass a second metric. */
  metric: MetricComparison | null | undefined;
  valueLabel: string;
  comparisonReason?: string | null;
  className?: string;
  metricKey?: string;
};

function HistogramBar({
  x = 0,
  y = 0,
  width = 0,
  height = 0,
  fill,
  index = 0,
  payload,
}: {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  fill?: string;
  index?: number;
  payload?: { highlight?: boolean };
}) {
  const highlight = Boolean(payload?.highlight);
  return (
    <motion.rect
      x={x}
      y={y}
      width={width}
      height={height}
      fill={fill}
      initial={{ scaleY: 0, opacity: highlight ? 0 : 1 }}
      animate={{ scaleY: 1, opacity: 1 }}
      style={{ originX: 0.5, originY: 1 }}
      transition={{ duration: DURATION.base, ease: EASE, delay: index * STAGGER }}
    />
  );
}

export function CorpusHistogram({
  title,
  metric,
  valueLabel,
  comparisonReason,
  className,
  metricKey,
}: CorpusHistogramProps) {
  const key = metricKey ?? title;
  const silverId = useBarSilverId();
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
        <p className="mt-2" data-testid={`corpus-reason-${key}`}>
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
      className={className}
      table={
        <HiddenTable
          caption={`${title} corpus histogram`}
          columns={["bin", "count", "this app"]}
          rows={rows.map((row) => [row.bin, row.count, row.highlight ? "yes" : "no"])}
        />
      }
    >
      <p className="sr-only" data-testid={`histogram-highlight-count-${key}`}>
        {highlighted.length}
      </p>
      <p className="sr-only" data-testid={`corpus-label-${key}`}>
        This app: {valueLabel}
        {percentileText ? ` (${percentileText})` : ""}
      </p>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
          <BarSilverDefs id={silverId} />
          <XAxis dataKey="bin" tick={{ fontSize: 11, fill: "var(--text-faint)" }} axisLine={false} tickLine={false} />
          <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: "var(--text-faint)" }} axisLine={false} tickLine={false} width={28} />
          <Tooltip />
          <Bar dataKey="count" isAnimationActive={false} name="corpus apps" shape={HistogramBar}>
            {rows.map((row) => (
              <Cell
                key={row.bin}
                fill={row.highlight ? CHART_ACCENT : `url(#${silverId})`}
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
