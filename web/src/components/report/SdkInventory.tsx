"use client";

import { AnimatePresence, motion } from "motion/react";
import { useState } from "react";
import { DURATION, EASE } from "@/lib/motion";
import type { Report } from "@/lib/report-types";
import { asArray, asRecord, display, matchesFilter } from "@/lib/report-access";
import { FilterInput } from "./controls";

export function SdkInventory({ report }: { report: Report }) {
  const [filter, setFilter] = useState("");
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const entries = asArray(report.sdk_inventory).map(asRecord);
  const rows = entries
    .map((entry, index) => ({ entry, index, packages: asArray(entry.packages) }))
    .filter(({ entry, packages }) =>
      matchesFilter(filter, entry.sdk_name, entry.sdk_category, ...packages),
    );

  function toggle(index: number) {
    setExpanded((current) => {
      const next = new Set(current);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  }

  return (
    <section aria-labelledby="sdk-inventory-heading" className="card">
      <h2 id="sdk-inventory-heading" className="text-2xl">
        SDK inventory
      </h2>
      <p className="mb-3 text-sm">{entries.length} SDK entries attributed by package namespace.</p>
      <FilterInput label="Filter SDKs" value={filter} onChange={setFilter} />
      <div className="overflow-x-auto">
        <table className="data-table">
          <caption className="sr-only">SDK inventory</caption>
          <thead>
            <tr>
              <th scope="col">SDK name</th>
              <th scope="col">SDK category</th>
              <th scope="col">Packages</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td colSpan={3}>—</td>
              </tr>
            ) : (
              rows.map(({ entry, index, packages }) => {
                const open = expanded.has(index);
                const listId = `sdk-packages-${index}`;
                return (
                  <tr key={index}>
                    <td>{display(entry.sdk_name)}</td>
                    <td>{display(entry.sdk_category)}</td>
                    <td>
                      <button
                        type="button"
                        className="btn-link"
                        aria-expanded={open}
                        aria-controls={listId}
                        onClick={() => toggle(index)}
                      >
                        {packages.length} {packages.length === 1 ? "package" : "packages"}
                      </button>
                      <AnimatePresence>
                        {open ? (
                          <motion.div
                            key="packages"
                            layout
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            transition={{ duration: DURATION.fast, ease: EASE }}
                          >
                            <ul id={listId} className="mt-1 list-disc pl-6 font-mono text-sm">
                              {packages.map((pkg, i) => (
                                <li key={i} className="break-all">
                                  {display(pkg)}
                                </li>
                              ))}
                            </ul>
                          </motion.div>
                        ) : null}
                      </AnimatePresence>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
