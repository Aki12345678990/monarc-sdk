import { useId, type ReactNode } from "react";

export function ChartFrame({
  title,
  caption,
  empty,
  table,
  legend,
  children,
}: {
  title: string;
  caption: string;
  empty: boolean;
  table: ReactNode;
  legend?: ReactNode;
  children: ReactNode;
}) {
  const captionId = useId();
  const headingId = useId();
  return (
    <section aria-labelledby={headingId} className="card">
      <h3 id={headingId} className="text-xl">
        {title}
      </h3>
      {empty ? (
        <p className="mt-2">No data</p>
      ) : (
        <>
          <div className="mt-2 h-56 w-full" aria-describedby={captionId}>
            {children}
          </div>
          {legend}
          <p id={captionId} className="mt-2 text-sm">
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
