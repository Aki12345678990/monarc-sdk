import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import fixture from "@/test/fixtures/report.json";
import type { Report } from "@/lib/report-types";
import { ReportView } from "./ReportView";

const report = fixture as Report;
const json = JSON.stringify(fixture, null, 2);
const FORBIDDEN = /score|tier|verdict|malicious|\bsafe\b|critical|high risk|low risk/i;
const ALLOWED_LIMITATION = "This is not a malware verdict.";

function renderReport(value: Report = report) {
  return render(<ReportView report={value} json={json} />);
}

describe("ReportView", () => {
  test("renders package, D value, hosts, SDK inventory and indicator statuses", () => {
    renderReport();
    expect(screen.getByRole("heading", { level: 1, name: "org.example.synthetic" })).toBeTruthy();
    expect(screen.getByTestId("d-value").textContent).toBe("12.50%");
    expect(screen.getByText("namespace breadth, not code volume; lower bound in obfuscated apps", { exact: false })).toBeTruthy();
    expect(screen.getByTestId("n-value").textContent).toBe("4");
    expect(screen.getByText("api.example.org")).toBeTruthy();
    expect(screen.getByText("203.0.113.7")).toBeTruthy();
    expect(screen.getAllByText("Acme Analytics").length).toBe(2);
    expect(screen.getByText("Fabrikam Crash Reporter")).toBeTruthy();
    expect(screen.getByTestId("indicator-P-status").textContent).toBe("Not implemented");
    expect(screen.getByTestId("indicator-A-status").textContent).toBe("Unavailable");
    expect(screen.getByTestId("indicator-M-status").textContent).toBe("Not implemented");
    expect(screen.getByTestId("indicator-D-status").textContent).toBe("OK");
    expect(screen.getByTestId("indicator-N-status").textContent).toBe("OK");
    expect(screen.getByText("Requested permissions (raw, unclassified)")).toBeTruthy();
    expect(screen.getByText("android.permission.CAMERA")).toBeTruthy();
    expect(screen.getByText(report.comparison_reason as string)).toBeTruthy();
    expect(screen.getByText("org.example.synthetic.MainActivity")).toBeTruthy();
  });

  test("renders limitations verbatim", () => {
    renderReport();
    const items = within(screen.getByTestId("limitations")).getAllByRole("listitem");
    expect(items.map((item) => item.textContent)).toEqual(report.limitations);
  });

  test("shows definition_source on every indicator that has one", () => {
    renderReport();
    for (const letter of ["A", "N", "D"] as const) {
      const source = report.indicators?.[letter].definition_source;
      expect(source).toBeTruthy();
      expect(screen.getByText(source as string)).toBeTruthy();
    }
  });

  test("expands an SDK's package list", () => {
    renderReport();
    fireEvent.click(screen.getByRole("button", { name: "3 packages" }));
    expect(screen.getByText("com.fabrikam.crash.ndk")).toBeTruthy();
  });

  test("filters hosts", () => {
    renderReport();
    fireEvent.change(screen.getByLabelText("Filter hosts"), { target: { value: "contoso" } });
    expect(screen.getByText("tiles.contoso-maps.example")).toBeTruthy();
    expect(screen.queryByText("api.example.org")).toBeNull();
  });

  test("rendered text contains no grading language", () => {
    const { container } = renderReport();
    const text = container.textContent ?? "";
    expect(text).toContain(ALLOWED_LIMITATION);
    const withoutAllowed = text.split(ALLOWED_LIMITATION).join(" ");
    expect(withoutAllowed.match(FORBIDDEN)).toBeNull();
  });

  test("tolerates a report with missing optional fields", () => {
    const sparse: Report = {
      indicators: {
        P: { status: "not_implemented" },
        A: { status: "unavailable" },
        N: { status: "ok" },
        M: { status: "not_implemented" },
        D: { status: "ok" },
      },
    };
    renderReport(sparse);
    expect(screen.getByRole("heading", { level: 1, name: "—" })).toBeTruthy();
    expect(screen.getByTestId("d-value").textContent).toBe("—");
    expect(screen.getByTestId("n-value").textContent).toBe("—");
  });
});
