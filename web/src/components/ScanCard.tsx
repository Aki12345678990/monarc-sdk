"use client";

import { motion, useReducedMotion } from "motion/react";
import { EASE, LOOP } from "@/lib/motion";

export function ScanCard({ elapsed }: { elapsed: string }) {
  const reduce = useReducedMotion();
  return (
    <div aria-hidden className="mt-4 flex items-start gap-4">
      <div className="relative h-24 w-20 overflow-hidden rounded border border-edge-hi bg-bg-2">
        <div className="absolute inset-x-2 top-3 h-1 bg-data-1/40" />
        <div className="absolute inset-x-2 top-6 h-1 bg-data-1/25" />
        <div className="absolute inset-x-2 top-9 h-1 bg-data-1/15" />
        {reduce ? null : (
          <motion.div
            className="absolute left-0 right-0 h-0.5 bg-accent"
            animate={{ y: [8, 80, 8] }}
            transition={{ duration: LOOP.sweep, repeat: Infinity, ease: EASE }}
          />
        )}
      </div>
      <p className="text-sm">Elapsed {elapsed}</p>
    </div>
  );
}
