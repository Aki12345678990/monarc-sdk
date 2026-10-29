import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import fixture from "@/test/fixtures/report.json";
import type { Report } from "@/lib/report-types";
import { ReportView } from "./ReportView";
import { CorpusHistogram, type CorpusHistogramProps } from "./charts/CorpusHistogram";

const report = fixture as Report;
const json = JSON.stringify(fixture, null, 2);
const FORBIDDEN = /score|tier|verdict|malicious|\bsafe\b|critical|high risk|low risk|risk score|rating|grade/i;
const ALLOWED_LIMITATION = "This is not a malware verdict.";

function renderReport(value: Report = report) {
  return render(<ReportView report={value} json={json} />);
}

describe("ReportView", () => {
  test("renders package, D value, hosts, SDK inventory and indicator statuses", () => {
    renderReport();
    expect(screen.getByRole("heading", { level: 1, name: "org.example.synthetic" })).toBeTruthy();
    expect(screen.getByTestId("d-value").textContent).toBe("12.50%");
    expect(
      screen.getByText("namespace breadth, not code volume; lower bound in obfuscated apps", {
        exact: false,
      }),
    ).toBeTruthy();
    expect(screen.getByTestId("n-value").textContent).toBe("4");
    expect(screen.getByText("api.example.org")).toBeTruthy();
    expect(screen.getByText("203.0.113.7")).toBeTruthy();
    expect(screen.getAllByText("Acme Analytics").length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("Fabrikam Crash Reporter").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByTestId("indicator-P-status").textContent).toBe("Not implemented");
    expect(screen.getByTestId("indicator-A-status").textContent).toBe("Unavailable");
    expect(screen.getByTestId("indicator-M-status").textContent).toBe("Not implemented");
    expect(screen.getByTestId("indicator-D-status").textContent).toBe("OK");
    expect(screen.getByTestId("indicator-N-status").textContent).toBe("OK");
    expect(screen.getByText("Requested permissions (raw, unclassified)")).toBeTruthy();
    expect(screen.getByText("android.permission.CAMERA")).toBeTruthy();
    expect(screen.getByText("org.example.synthetic.MainActivity")).toBeTruthy();
  });

  test("exposure profile renders tiles and percentiles", () => {
    renderReport();
    expect(screen.getByRole("heading", { name: "Exposure profile" })).toBeTruthy();
    expect(screen.getByTestId("tile-d").textContent).toBe("12.5%");
    expect(screen.getByTestId("tile-d-percentile").textContent).toBe(
      "higher than 22.5% of corpus apps",
    );
    expect(screen.getByTestId("tile-sdks").textContent).toBe("3");
    expect(screen.getByTestId("tile-sdks-percentile").textContent).toBe(
      "higher than 8.0% of corpus apps",
    );
    expect(screen.getByTestId("tile-n").textContent).toBe("4");
    expect(screen.getByTestId("tile-n-percentile").textContent).toBe(
      "higher than 15.0% of corpus apps",
    );
    expect(screen.getByTestId("tile-frameworks").textContent).toBe("flutter");
    expect(screen.getByTestId("chip-p").textContent).toBe("P Not implemented");
    expect(screen.getByTestId("chip-a").textContent).toBe("A Unavailable");
    expect(screen.getByTestId("chip-m").textContent).toBe("M Not implemented");
    expect(screen.getByTestId("exposure-caption").textContent).toContain(
      "Percentile compares this app with the corpus one measure at a time. It is not a risk measure.",
    );
  });

  test("histogram highlights exactly one bin when app_bin is set", () => {
    renderReport();
    expect(screen.getByTestId("histogram-highlight-count-D").textContent).toBe("1");
    expect(screen.getByTestId("histogram-highlight-count-N").textContent).toBe("1");
    expect(screen.getByTestId("histogram-highlight-count-Distinct SDKs").textContent).toBe("1");
  });

  test("shows comparison_reason when comparison is null", () => {
    const without: Report = { ...report, comparison: null, comparison_reason: "Corpus reference unavailable" };
    renderReport(without);
    expect(screen.getByTestId("corpus-position-reason").textContent).toBe(
      "Corpus reference unavailable",
    );
  });

  test("CorpusHistogram props take a single metric", () => {
    const props: CorpusHistogramProps = {
      title: "D",
      metric: report.comparison?.metrics.D,
      valueLabel: "12.5%",
    };
    expect(Object.keys(props)).toEqual(["title", "metric", "valueLabel"]);
    expect("metrics" in props).toBe(false);
    const { container } = render(
      <CorpusHistogram title={props.title} metric={props.metric} valueLabel={props.valueLabel} />,
    );
    expect(container.querySelectorAll("[data-testid='histogram-highlight-count-D']")).toHaveLength(1);
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
