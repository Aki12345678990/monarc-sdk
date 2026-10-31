import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(fileURLToPath(import.meta.url));
const cssPath = join(ROOT, "..", "src", "app", "globals.css");
const css = readFileSync(cssPath, "utf8");
const rootBlock = css.match(/:root\s*\{([\s\S]*?)\n\}/);
if (!rootBlock) {
  console.error("Cannot find :root tokens in globals.css");
  process.exit(1);
}

const tokens = {};
for (const match of rootBlock[1].matchAll(/--([a-z0-9-]+):\s*([^;]+);/g)) {
  tokens[match[1]] = match[2].trim();
}

function parseHex(value) {
  const hex = value.replace("#", "").trim();
  if (!/^[0-9a-fA-F]{6}$/.test(hex)) return null;
  return [
    Number.parseInt(hex.slice(0, 2), 16),
    Number.parseInt(hex.slice(2, 4), 16),
    Number.parseInt(hex.slice(4, 6), 16),
  ];
}

function parseRgba(value) {
  const match = value.match(/rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)(?:\s*,\s*([\d.]+))?\s*\)/);
  if (!match) return null;
  return {
    rgb: [Number(match[1]), Number(match[2]), Number(match[3])],
    a: match[4] === undefined ? 1 : Number(match[4]),
  };
}

function channel(c) {
  const x = c / 255;
  return x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4;
}

function luminance(rgb) {
  return 0.2126 * channel(rgb[0]) + 0.7152 * channel(rgb[1]) + 0.0722 * channel(rgb[2]);
}

function contrast(a, b) {
  const l1 = luminance(a);
  const l2 = luminance(b);
  const hi = Math.max(l1, l2);
  const lo = Math.min(l1, l2);
  return (hi + 0.05) / (lo + 0.05);
}

function composite(fg, bg, alpha) {
  return [
    fg[0] * alpha + bg[0] * (1 - alpha),
    fg[1] * alpha + bg[1] * (1 - alpha),
    fg[2] * alpha + bg[2] * (1 - alpha),
  ];
}

function hexOf(rgb) {
  return `#${rgb.map((c) => Math.round(c).toString(16).padStart(2, "0")).join("")}`;
}

const bg = parseHex(tokens.bg);
const text = parseHex(tokens.text);
const muted = parseHex(tokens["text-muted"]);
const accent = parseHex(tokens.accent);
const glass = parseRgba(tokens.glass);
const glassStrong = parseRgba(tokens["glass-strong"]);
const buttonInk = parseHex("#0b0c0f");
const chromeDarkest = parseHex("#8d94a0");

if (!bg || !text || !muted || !accent || !glass || !glassStrong || !buttonInk || !chromeDarkest) {
  console.error("Could not parse required tokens", { tokens });
  process.exit(1);
}

const glassOverBg = composite(glass.rgb, bg, glass.a);
const strongOverBg = composite(glassStrong.rgb, bg, glassStrong.a);

const TEXT_MIN = 4.5;
const MUTED_MIN = 4.5;
const ACCENT_MIN = 4.5;
const BUTTON_MIN = 4.5;

const checks = [
  { name: "--text on glass∘--bg", fg: text, bg: glassOverBg, min: TEXT_MIN, token: "text" },
  { name: "--text-muted on glass∘--bg", fg: muted, bg: glassOverBg, min: MUTED_MIN, token: "text-muted" },
  { name: "--accent on glass∘--bg", fg: accent, bg: glassOverBg, min: ACCENT_MIN, token: "accent" },
  { name: "--text on glass-strong∘--bg", fg: text, bg: strongOverBg, min: TEXT_MIN, token: "text" },
  { name: "--text-muted on glass-strong∘--bg", fg: muted, bg: strongOverBg, min: MUTED_MIN, token: "text-muted" },
  { name: "--accent on glass-strong∘--bg", fg: accent, bg: strongOverBg, min: ACCENT_MIN, token: "accent" },
  { name: "#0b0c0f on chrome darkest #8d94a0", fg: buttonInk, bg: chromeDarkest, min: BUTTON_MIN, token: "chrome-ink" },
];

let failed = false;
const rows = [];
for (const check of checks) {
  const ratio = contrast(check.fg, check.bg);
  const ok = ratio + 1e-9 >= check.min;
  if (!ok) failed = true;
  rows.push({
    name: check.name,
    fg: hexOf(check.fg),
    bg: hexOf(check.bg),
    ratio: Number(ratio.toFixed(2)),
    min: check.min,
    ok,
  });
}

console.log("Glass composites");
console.log(`  glass∘bg        ${hexOf(glassOverBg)}`);
console.log(`  glass-strong∘bg ${hexOf(strongOverBg)}`);
console.log("");
for (const row of rows) {
  const mark = row.ok ? "PASS" : "FAIL";
  console.log(`${mark}  ${row.name}: ${row.ratio}:1 (min ${row.min}:1)  fg ${row.fg} on ${row.bg}`);
}

if (failed) {
  console.error("\nOne or more contrast checks failed. Adjust token lightness only.");
  process.exit(1);
}

process.exit(0);
