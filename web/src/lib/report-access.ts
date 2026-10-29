// Narrowing helpers for the untyped parts of the Report contract
// (IndicatorResult.details, frameworks, sdk_inventory are `unknown` in report-types.ts).

export const MISSING = "—";

export type UnknownRecord = Record<string, unknown>;

export function asRecord(value: unknown): UnknownRecord {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? (value as UnknownRecord)
    : {};
}

export function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

export function asString(value: unknown): string | null {
  return typeof value === "string" ? value : null;
}

export function asNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

/** Text for a value that may be absent: missing or null renders as an em dash. */
export function display(value: unknown): string {
  if (value === undefined || value === null || value === "") return MISSING;
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return JSON.stringify(value);
}

/** Text for a raw fact exactly as the report states it; only an absent key renders as an em dash. */
export function rawFact(value: unknown): string {
  if (value === undefined) return MISSING;
  if (typeof value === "string") return value;
  return JSON.stringify(value);
}

export function formatPercent(value: number | null): string {
  if (value === null) return MISSING;
  return `${value.toFixed(2)}%`;
}

export function formatBytes(value: number | null | undefined): string {
  if (value === null || value === undefined) return MISSING;
  const mib = value / (1024 * 1024);
  return `${value.toLocaleString("en-GB")} bytes (${mib.toFixed(2)} MiB)`;
}

export function matchesFilter(filter: string, ...fields: unknown[]): boolean {
  const needle = filter.trim().toLowerCase();
  if (needle === "") return true;
  return fields.some((field) => display(field).toLowerCase().includes(needle));
}
