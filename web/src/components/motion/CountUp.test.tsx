import { render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import { CountUp } from "./CountUp";

describe("CountUp", () => {
  test("under reduced motion renders the final formatted value immediately", () => {
    render(<CountUp value={12.5} format={(n) => `${n.toFixed(1)}%`} />);
    const node = screen.getByLabelText("12.5%");
    expect(node.textContent).toBe("12.5%");
    expect(node.getAttribute("aria-label")).toBe("12.5%");
  });
});
