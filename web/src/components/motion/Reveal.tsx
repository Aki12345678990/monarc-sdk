"use client";

import { motion } from "motion/react";
import type { ReactNode } from "react";
import { fadeUpBelow } from "@/lib/motion";

export function Reveal({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <motion.div
      className={className}
      variants={fadeUpBelow}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, amount: 0.12 }}
    >
      {children}
    </motion.div>
  );
}
