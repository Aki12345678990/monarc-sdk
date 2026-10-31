"use client";

import {
  useEffect,
  useId,
  useRef,
  useState,
  type KeyboardEvent,
  type ReactNode,
  type RefObject,
} from "react";

const FOCUSABLE = "a[href],button:not([disabled]),input:not([disabled]),textarea,select,[tabindex]:not([tabindex='-1'])";

export function InfoTooltip({ label, description }: { label: string; description: string }) {
  const id = useId();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    function onKey(event: globalThis.KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open]);

  return (
    <span className="info-tooltip">
      <button
        type="button"
        className="btn-link text-sm"
        aria-label={`About ${label}`}
        aria-expanded={open}
        aria-describedby={id}
        onMouseEnter={() => setOpen(true)}
        onFocus={() => setOpen(true)}
        onClick={() => setOpen((value) => !value)}
      >
        i
      </button>
      <span id={id} role="tooltip" className="info-tooltip-panel" hidden={!open}>
        {description}
      </span>
    </span>
  );
}

export function AboutSheet({
  open,
  onClose,
  returnTo,
  children,
}: {
  open: boolean;
  onClose: () => void;
  returnTo: RefObject<HTMLButtonElement | null>;
  children: ReactNode;
}) {
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const panel = panelRef.current;
    const first = panel?.querySelector<HTMLElement>(FOCUSABLE);
    first?.focus();

    function onKey(event: globalThis.KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        returnTo.current?.focus();
        return;
      }
      if (event.key !== "Tab" || !panel) return;
      const nodes = [...panel.querySelectorAll<HTMLElement>(FOCUSABLE)];
      if (nodes.length === 0) return;
      const firstNode = nodes[0];
      const lastNode = nodes[nodes.length - 1];
      if (event.shiftKey && document.activeElement === firstNode) {
        event.preventDefault();
        lastNode.focus();
      } else if (!event.shiftKey && document.activeElement === lastNode) {
        event.preventDefault();
        firstNode.focus();
      }
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose, returnTo]);

  if (!open) return <div hidden>{children}</div>;

  return (
    <>
      <button type="button" className="about-backdrop" aria-label="Close about sheet" onClick={() => { onClose(); returnTo.current?.focus(); }} />
      <div ref={panelRef} role="dialog" aria-modal="true" aria-labelledby="about-sheet-title" className="panel about-sheet">
        <div className="flex items-center justify-between gap-3">
          <h2 id="about-sheet-title" className="section-title">
            About these numbers
          </h2>
          <button type="button" className="btn-secondary" onClick={() => { onClose(); returnTo.current?.focus(); }}>
            Close
          </button>
        </div>
        <div className="mt-3 space-y-3">{children}</div>
      </div>
    </>
  );
}

export function Tabs({
  className,
  tabs,
}: {
  className?: string;
  tabs: Array<{ id: string; label: string; className?: string; node: ReactNode }>;
}) {
  const [selected, setSelected] = useState(0);
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);

  function select(index: number) {
    setSelected(index);
    tabRefs.current[index]?.focus();
  }

  function onKey(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "ArrowRight") {
      event.preventDefault();
      select((selected + 1) % tabs.length);
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      select((selected - 1 + tabs.length) % tabs.length);
    }
  }

  return (
    <div className={`tabs tabbed ${className ?? ""}`.trim()}>
      <div role="tablist" aria-label="Sections" onKeyDown={onKey}>
        {tabs.map((tab, index) => (
          <button
            key={tab.id}
            ref={(node) => {
              tabRefs.current[index] = node;
            }}
            type="button"
            role="tab"
            id={`tab-${tab.id}`}
            aria-selected={selected === index}
            aria-controls={`panel-${tab.id}`}
            tabIndex={selected === index ? 0 : -1}
            onClick={() => setSelected(index)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      {tabs.map((tab, index) => (
        <div
          key={tab.id}
          role="tabpanel"
          id={`panel-${tab.id}`}
          aria-labelledby={`tab-${tab.id}`}
          hidden={selected !== index}
          className={`tab-fade ${tab.className ?? ""}`.trim()}
        >
          {tab.node}
        </div>
      ))}
    </div>
  );
}
