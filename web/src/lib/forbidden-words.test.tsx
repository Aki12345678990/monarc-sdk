import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { extname, join } from "node:path";
import { render } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import Home from "@/app/page";
import MethodPage from "@/app/method/page";
import { MotionRoot } from "@/components/motion/MotionRoot";
import { StatusStepper } from "@/components/StatusStepper";
import { UploadForm } from "@/components/UploadForm";
import { ReportView } from "@/components/report/ReportView";
import fixture from "@/test/fixtures/report.json";
import type { JobStatus } from "./api";
import type { Report } from "./report-types";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: () => undefined }),
}));

const FORBIDDEN = /score|tier|verdict|malicious|\bsafe\b|critical|high risk|low risk/i;
const ALLOWED_LIMITATION = "This is not a malware verdict.";

const STATUSES: JobStatus[] = [
  "awaiting_upload",
  "queued",
  "running",
  "done",
  "rejected",
  "failed",
  "expired",
];

function walk(dir: string, acc: string[] = []): string[] {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) walk(path, acc);
    else acc.push(path);
  }
  return acc;
}

function hitsIn(text: string): string[] {
  const withoutAllowed = text.split(ALLOWED_LIMITATION).join(" ");
  return withoutAllowed.match(new RegExp(FORBIDDEN.source, "gi")) ?? [];
}

describe("forbidden words in rendered UI", () => {
  test("Home, Method, report, stepper and upload contain no forbidden words", () => {
    const surfaces = [
      render(<Home />).container,
      render(<MethodPage />).container,
      render(
        <MotionRoot>
          <ReportView report={fixture as Report} json={JSON.stringify(fixture)} />
        </MotionRoot>,
      ).container,
      render(<UploadForm />).container,
      ...STATUSES.map((status) => render(<StatusStepper status={status} elapsed="1 s" />).container),
    ];
    const allowListed: string[] = [];
    const hits: string[] = [];
    for (const node of surfaces) {
      const text = node.textContent ?? "";
      if (text.includes(ALLOWED_LIMITATION)) allowListed.push(ALLOWED_LIMITATION);
      hits.push(...hitsIn(text));
    }
    expect(new Set(allowListed)).toEqual(new Set([ALLOWED_LIMITATION]));
    expect(hits).toEqual([]);
  });

  test("component and page source strings have no extra forbidden words", () => {
    const src = join(process.cwd(), "src");
    expect(existsSync(src)).toBe(true);
    const files = walk(src).filter((path) => {
      const ext = extname(path);
      if (ext !== ".ts" && ext !== ".tsx") return false;
      if (path.endsWith(".test.ts") || path.endsWith(".test.tsx")) return false;
      return statSync(path).isFile();
    });
    const hits: string[] = [];
    for (const file of files) {
      const text = readFileSync(file, "utf8");
      for (const hit of hitsIn(text)) {
        hits.push(`${file}: ${hit}`);
      }
    }
    expect(hits).toEqual([]);
  });
});
