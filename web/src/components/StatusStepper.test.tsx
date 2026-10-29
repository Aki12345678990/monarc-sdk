import { render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import type { JobStatus } from "@/lib/api";
import { StatusStepper, stepperModel } from "./StatusStepper";

const CASES: Array<{ status: JobStatus; active: string }> = [
  { status: "awaiting_upload", active: "upload" },
  { status: "queued", active: "queued" },
  { status: "running", active: "analysing" },
  { status: "done", active: "done" },
  { status: "rejected", active: "rejected" },
  { status: "failed", active: "failed" },
  { status: "expired", active: "expired" },
];

describe("StatusStepper", () => {
  test.each(CASES)("active step for $status is $active", ({ status, active }) => {
    const model = stepperModel(status);
    expect(model.active).toBe(active);
    render(<StatusStepper status={status} />);
    expect(screen.getByTestId(`step-${active}`).getAttribute("data-active")).toBe(
      status === "done" ? "false" : "true",
    );
  });
});
