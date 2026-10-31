import { useId, type ReactNode } from "react";

export function ChartFrame({
  title,
  caption,
  empty,
  table,
  className,
  children,
}: {
  title: string;
  caption: string;
  empty: boolean;
  table: ReactNode;
  className?: string;
  children: ReactNode;
}) {
  const captionId = useId();
  const headingId = useId();
  return (
    <section aria-labelledby={headingId} className={`card chart-panel ${className ?? ""}`.trim()}>
      <h3 id={headingId} className="section-title">
        {title}
      </h3>
      {empty ? (
        <p className="mt-2">No data</p>
      ) : (
        <>
          <div className="chart-body mt-2 w-full" aria-describedby={captionId}>
            {children}
          </div>
          <p id={captionId} className="sr-only">
            {caption}
          </p>
          <div className="sr-only">{table}</div>
        </>
      )}
    </section>
  );
}

export function HiddenTable({
  caption,
  columns,
  rows,
}: {
  caption: string;
  columns: string[];
  rows: Array<Array<string | number>>;
}) {
  return (
    <table>
      <caption>{caption}</caption>
      <thead>
        <tr>
          {columns.map((column) => (
            <th key={column} scope="col">
              {column}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, index) => (
          <tr key={index}>
            {row.map((cell, cellIndex) => (
              <td key={cellIndex}>{cell}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
