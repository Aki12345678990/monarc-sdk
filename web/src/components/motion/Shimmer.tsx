"use client";

import { motion, useReducedMotion } from "motion/react";
import { EASE_LOOP, LOOP } from "@/lib/motion";

export function Shimmer({ className }: { className?: string }) {
  const reduce = useReducedMotion();
  return (
    <div className={`relative overflow-hidden ${className ?? ""}`}>
      {reduce ? null : (
        <motion.div
          aria-hidden
          className="absolute inset-y-0 w-1/3 bg-orange/30"
          animate={{ x: ["-120%", "320%"] }}
          transition={{ duration: LOOP.shimmer, repeat: Infinity, ease: EASE_LOOP }}
        />
      )}
    </div>
  );
}
