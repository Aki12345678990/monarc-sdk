import { render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import type { JobStatus } from "@/lib/api";
import { JOB_STATUS_LABELS } from "@/lib/labels";
import { StatusStepper, stepperModel } from "./StatusStepper";

const CASES: Array<{ status: JobStatus; active: JobStatus }> = [
  { status: "awaiting_upload", active: "awaiting_upload" },
  { status: "queued", active: "queued" },
  { status: "running", active: "running" },
  { status: "done", active: "done" },
  { status: "rejected", active: "rejected" },
  { status: "failed", active: "failed" },
  { status: "expired", active: "expired" },
];

describe("StatusStepper", () => {
  test.each(CASES)("active step for $status is $active", ({ status, active }) => {
    const model = stepperModel(status);
    expect(model.active).toBe(active);
    expect(model.steps.every((step) => step in JOB_STATUS_LABELS)).toBe(true);
    render(<StatusStepper status={status} elapsed="12 s" />);
    expect(screen.getByTestId(`step-${active}`).getAttribute("data-active")).toBe(
      status === "done" ? "false" : "true",
    );
    expect(screen.getByTestId(`step-${active}`).textContent).toContain(JOB_STATUS_LABELS[active]);
    if (status === "running") {
      expect(screen.getByTestId("step-elapsed").textContent).toBe("12 s");
    }
  });
});
