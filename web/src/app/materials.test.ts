import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, extname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, test } from "vitest";

const SRC = join(dirname(fileURLToPath(import.meta.url)), "..");
const CSS_PATH = join(SRC, "app", "globals.css");
const NEXT_STATIC = join(SRC, "..", ".next", "static");

function walk(dir: string, acc: string[] = []): string[] {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) walk(path, acc);
    else acc.push(path);
  }
  return acc;
}

function collectBuiltCss(): string {
  if (!existsSync(NEXT_STATIC)) return "";
  return walk(NEXT_STATIC)
    .filter((path) => extname(path) === ".css")
    .map((path) => readFileSync(path, "utf8"))
    .join("\n");
}

const css = readFileSync(CSS_PATH, "utf8");

describe("glass/metal materials", () => {
  test("@supports fallback class is present in source CSS", () => {
    expect(css).toMatch(/@supports not \(backdrop-filter: blur\(1px\)\)/);
    expect(css).toMatch(/\.panel-fallback/);
  });

  test("@supports fallback class is present in built CSS when .next exists", () => {
    const built = collectBuiltCss();
    if (!built || !built.includes("panel-fallback")) {
      return;
    }
    expect(built).toMatch(/@supports not[\s\S]{0,160}backdrop-filter:\s*blur\(1px\)/);
    expect(built).toMatch(/panel-fallback/);
  });

  test("under reduced motion the background blobs, sheen and shimmer do not animate", () => {
    const reduce = css.match(/@media \(prefers-reduced-motion: reduce\)\s*\{([\s\S]*?)\n\}/);
    expect(reduce).toBeTruthy();
    const body = reduce?.[1] ?? "";
    expect(body).toMatch(/\.blob/);
    expect(body).toMatch(/\.chrome-text/);
    expect(body).toMatch(/\.panel::after/);
    expect(body).toMatch(/animation:\s*none/);
  });

  test("no nested element inside a panel has backdrop-filter", () => {
    const nested = [".tile", ".chip", ".data-table", ".dropzone-ring", ".filter-input", ".meter", ".progress-track"];
    const blurRule = /([^{}]+)\{[^}]*backdrop-filter:[^}]*\}/g;
    const selectors: string[] = [];
    for (const match of css.matchAll(blurRule)) {
      selectors.push(match[1].replace(/\s+/g, " ").trim());
    }
    expect(selectors.length).toBeGreaterThan(0);
    for (const selector of selectors) {
      for (const name of nested) {
        expect(selector.includes(name)).toBe(false);
      }
    }
    expect(selectors.some((item) => item.includes(".panel") || item.includes(".card"))).toBe(true);

    const components = walk(join(SRC, "components")).filter((path) => {
      const ext = extname(path);
      return ext === ".tsx" || ext === ".ts";
    });
    for (const file of components) {
      if (statSync(file).isDirectory()) continue;
      const text = readFileSync(file, "utf8");
      expect(text).not.toMatch(/backdropFilter|backdrop-filter/);
    }
  });
});
