export const DURATION = {
  fast: 0.15,
  base: 0.3,
  slow: 0.6,
} as const;

export const EASE = [0.22, 1, 0.36, 1] as const;

export const SPRING = { type: "spring" as const, stiffness: 280, damping: 24 };
export const SPRING_SOFT = { type: "spring" as const, stiffness: 180, damping: 22 };

export const STAGGER = 0.05;

export const LOOP = {
  breathe: 2,
  sweep: 1.8,
  shimmer: 1.2,
} as const;

export const EASE_LOOP = "linear" as const;

export const fadeUp = {
  hidden: { opacity: 0.6, y: 16 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: DURATION.base, ease: EASE },
  },
};

export const fadeUpBelow = {
  hidden: { opacity: 0, y: 16 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: DURATION.base, ease: EASE },
  },
};

export const fadeIn = {
  hidden: { opacity: 0.6 },
  show: {
    opacity: 1,
    transition: { duration: DURATION.base, ease: EASE },
  },
};

export const scaleIn = {
  hidden: { opacity: 0, scale: 0.96 },
  show: {
    opacity: 1,
    scale: 1,
    transition: { duration: DURATION.fast, ease: EASE },
  },
};

export const staggerContainer = {
  hidden: {},
  show: {
    transition: { staggerChildren: STAGGER },
  },
};

export const RECHARTS_DURATION_MS = DURATION.base * 1000;
export const RECHARTS_EASING = "cubic-bezier(0.22, 1, 0.36, 1)";
