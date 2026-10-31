import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, extname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WEB = join(dirname(fileURLToPath(import.meta.url)), "..");
const STATIC = join(WEB, ".next", "static");

function walk(dir, acc = []) {
  if (!existsSync(dir)) return acc;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) walk(path, acc);
    else acc.push(path);
  }
  return acc;
}

const css = walk(STATIC)
  .filter((path) => extname(path) === ".css")
  .map((path) => readFileSync(path, "utf8"))
  .join("\n");

if (!css) {
  console.error("No built CSS under .next/static");
  process.exit(1);
}

const hasSupports = /@supports not[\s\S]{0,160}backdrop-filter:\s*blur\(1px\)/.test(css);
const hasFallback = css.includes("panel-fallback");
if (!hasSupports || !hasFallback) {
  console.error("Built CSS missing @supports fallback / .panel-fallback", {
    hasSupports,
    hasFallback,
  });
  process.exit(1);
}

const reduce = css.match(/prefers-reduced-motion:\s*reduce[\s\S]{0,800}/);
if (!reduce || !/animation:\s*none/.test(reduce[0])) {
  console.error("Built CSS missing reduced-motion animation:none for materials");
  process.exit(1);
}

console.log("PASS  built CSS contains @supports .panel-fallback");
console.log("PASS  built CSS reduced-motion disables material animations");
process.exit(0);
