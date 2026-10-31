"use client";

import { useId, type ReactNode } from "react";
import { CountUp } from "@/components/motion/CountUp";

export const PAGE_SIZE = 100;

export function FilterInput({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  const id = useId();
  return (
    <div className="mb-3 flex flex-wrap items-center gap-2">
      <label htmlFor={id} className="text-sm font-semibold">
        {label}
      </label>
      <input
        id={id}
        type="search"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="filter-input"
      />
    </div>
  );
}

export function ShowMore({
  shown,
  total,
  onMore,
  noun,
}: {
  shown: number;
  total: number;
  onMore: () => void;
  noun: string;
}) {
  return (
    <div className="mt-2 flex flex-wrap items-center gap-3 text-sm">
      <span>
        Showing <CountUp value={Math.min(shown, total)} format={(n) => String(Math.round(n))} /> of{" "}
        <CountUp value={total} format={(n) => String(Math.round(n))} /> {noun}
      </span>
      {shown < total ? (
        <button type="button" onClick={onMore} className="btn-secondary">
          Show {Math.min(PAGE_SIZE, total - shown)} more
        </button>
      ) : null}
    </div>
  );
}

export function KeyValueTable({
  caption,
  rows,
}: {
  caption: string;
  rows: Array<[string, ReactNode]>;
}) {
  return (
    <table className="data-table">
      <caption className="sr-only">{caption}</caption>
      <tbody>
        {rows.map(([key, value]) => (
          <tr key={key}>
            <th scope="row" className="font-mono text-sm font-normal">
              {key}
            </th>
            <td className="font-mono text-sm break-all">{value}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
