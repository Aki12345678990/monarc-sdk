import { readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WEB = join(dirname(fileURLToPath(import.meta.url)), "..");
const NEXT = join(WEB, ".next");

function firstLoad(routeManifestRel) {
  const bm = JSON.parse(readFileSync(join(NEXT, "build-manifest.json"), "utf8"));
  const files = new Set([...(bm.polyfillFiles || []), ...bm.rootMainFiles]);
  const text = readFileSync(join(NEXT, routeManifestRel), "utf8");
  for (const match of text.matchAll(/\/_next\/(static\/chunks\/[^"'\\]+\.js)/g)) {
    files.add(match[1]);
  }
  let bytes = 0;
  const missing = [];
  const listed = [];
  for (const file of files) {
    try {
      const size = statSync(join(NEXT, file)).size;
      bytes += size;
      listed.push([size, file]);
    } catch {
      missing.push(file);
    }
  }
  listed.sort((a, b) => b[0] - a[0]);
  return {
    files: files.size,
    bytes,
    kB: Number((bytes / 1024).toFixed(1)),
    missing,
    top: listed.slice(0, 8),
  };
}

const label = process.argv[2] ?? "CURRENT";
const home = firstLoad(join("server", "app", "page_client-reference-manifest.js"));
const job = firstLoad(join("server", "app", "jobs", "[id]", "page_client-reference-manifest.js"));

console.log(`First Load JS (${label})`);
console.log(`  /            ${home.kB} kB  (${home.files} files, ${home.bytes} bytes)`);
console.log(`  /jobs/[id]   ${job.kB} kB  (${job.files} files, ${job.bytes} bytes)`);
if (home.missing.length || job.missing.length) {
  console.log("  missing", [...home.missing, ...job.missing]);
}
console.log("  / top", home.top);
console.log("  /jobs top", job.top);

const baseline = { "/": 726.5, "/jobs/[id]": 1120.1 };
const over = [];
if (home.kB > baseline["/"]) over.push(`/: ${home.kB} > ${baseline["/"]}`);
if (job.kB > baseline["/jobs/[id]"]) over.push(`/jobs/[id]: ${job.kB} > ${baseline["/jobs/[id]"]}`);
if (over.length) {
  console.error("BUDGET FAIL", over);
  process.exit(1);
}
console.log("BUDGET PASS  every route ≤ Phase 0 baseline");
