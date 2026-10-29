"use client";

import { animate, useMotionValue, useReducedMotion, useTransform } from "motion/react";
import { useEffect, useState } from "react";
import { DURATION, EASE } from "@/lib/motion";

export function CountUp({
  value,
  format,
  className,
}: {
  value: number;
  format: (value: number) => string;
  className?: string;
}) {
  const reduce = useReducedMotion();
  const final = format(value);
  const motionValue = useMotionValue(0);
  const formatted = useTransform(motionValue, (latest) => format(latest));
  const [text, setText] = useState(format(0));

  useEffect(() => {
    if (reduce) {
      return;
    }
    motionValue.set(0);
    const controls = animate(motionValue, value, {
      duration: DURATION.slow,
      ease: EASE,
    });
    const unsubscribe = formatted.on("change", setText);
    return () => {
      controls.stop();
      unsubscribe();
    };
  }, [value, reduce, motionValue, formatted]);

  return (
    <span className={className} aria-label={final}>
      {reduce ? final : text}
    </span>
  );
}
