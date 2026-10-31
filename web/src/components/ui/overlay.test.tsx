import { fireEvent, render, screen } from "@testing-library/react";
import { useRef, useState } from "react";
import { describe, expect, test } from "vitest";
import { MotionRoot } from "@/components/motion/MotionRoot";
import fixture from "@/test/fixtures/report.json";
import type { Report } from "@/lib/report-types";
import { ReportView } from "@/components/report/ReportView";
import { AboutSheet, InfoTooltip, Tabs } from "./overlay";

const report = fixture as Report;
const json = JSON.stringify(fixture);

function SheetHarness() {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLButtonElement>(null);
  return (
    <>
      <button ref={ref} type="button" onClick={() => setOpen(true)}>
        About these numbers
      </button>
      <AboutSheet open={open} onClose={() => setOpen(false)} returnTo={ref}>
        <button type="button">First</button>
        <button type="button">Last</button>
      </AboutSheet>
    </>
  );
}

describe("bento overlays", () => {
  test("tooltip opens on focus, closes on Esc, and exposes description via aria-describedby", () => {
    render(<InfoTooltip label="SDK footprint" description="namespace breadth, not code volume; lower bound in obfuscated apps" />);
    const button = screen.getByRole("button", { name: "About SDK footprint" });
    const tooltipId = button.getAttribute("aria-describedby");
    expect(tooltipId).toBeTruthy();
    expect(document.getElementById(tooltipId as string)?.textContent).toBe(
      "namespace breadth, not code volume; lower bound in obfuscated apps",
    );
    button.focus();
    fireEvent.focus(button);
    expect(screen.getByRole("tooltip").hidden).toBe(false);
    fireEvent.keyDown(document, { key: "Escape" });
    expect(screen.getByRole("tooltip", { hidden: true }).hidden).toBe(true);
  });

  test("about sheet traps focus, closes on Esc, and returns focus to the button", () => {
    render(<SheetHarness />);
    const trigger = screen.getByRole("button", { name: "About these numbers" });
    fireEvent.click(trigger);
    const dialog = screen.getByRole("dialog");
    expect(dialog).toBeTruthy();
    const first = screen.getByRole("button", { name: "Close" });
    const last = screen.getByRole("button", { name: "Last" });
    last.focus();
    fireEvent.keyDown(document, { key: "Tab" });
    expect(document.activeElement).toBe(first);
    first.focus();
    fireEvent.keyDown(document, { key: "Tab", shiftKey: true });
    expect(document.activeElement).toBe(last);
    fireEvent.keyDown(document, { key: "Escape" });
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(document.activeElement).toBe(trigger);
  });

  test("tabs expose roles, move with arrows, and hide unselected panels", () => {
    render(
      <Tabs
        tabs={[
          { id: "a", label: "Footprint", node: <p>Footprint panel</p> },
          { id: "b", label: "Hosts", node: <p>Hosts panel</p> },
          { id: "c", label: "Categories", node: <p>Categories panel</p> },
        ]}
      />,
    );
    const tabs = screen.getAllByRole("tab");
    expect(tabs.map((tab) => tab.getAttribute("aria-selected"))).toEqual(["true", "false", "false"]);
    expect(screen.getByRole("tabpanel").textContent).toContain("Footprint panel");
    expect((screen.getByText("Hosts panel").closest("[role='tabpanel']") as HTMLElement).hidden).toBe(true);
    fireEvent.keyDown(screen.getByRole("tablist"), { key: "ArrowRight" });
    expect(tabs[1].getAttribute("aria-selected")).toBe("true");
    expect((screen.getByText("Hosts panel").closest("[role='tabpanel']") as HTMLElement).hidden).toBe(false);
    expect((screen.getByText("Footprint panel").closest("[role='tabpanel']") as HTMLElement).hidden).toBe(true);
  });

  test("chart panels and table panels use the fixed-height classes", () => {
    const { container } = render(
      <MotionRoot>
        <ReportView report={report} json={json} />
      </MotionRoot>,
    );
    const charts = container.querySelectorAll(".chart-panel");
    const tables = container.querySelectorAll(".table-panel");
    expect(charts.length).toBeGreaterThanOrEqual(2);
    expect(tables.length).toBeGreaterThanOrEqual(2);
    for (const node of charts) {
      expect(node.className).toContain("chart-panel");
    }
    for (const node of tables) {
      expect(node.className).toContain("table-panel");
    }
  });
});
