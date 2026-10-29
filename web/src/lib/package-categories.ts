export const PACKAGE_CATEGORIES = [
  "toolchain",
  "framework",
  "sdk",
  "first_party",
  "obfuscated",
  "unattributed_third_party",
] as const;

export type PackageCategory = (typeof PACKAGE_CATEGORIES)[number];
