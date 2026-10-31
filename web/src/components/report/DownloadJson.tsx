"use client";

export function DownloadJson({ json, filename }: { json: string; filename: string }) {
  function download() {
    const url = URL.createObjectURL(new Blob([json], { type: "application/json" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  }

  return (
    <button type="button" onClick={download} className="btn-primary inline-flex items-center gap-2" aria-label="Download JSON report">
      <svg viewBox="0 0 24 24" className="h-4 w-4" aria-hidden>
        <path d="M12 4v10m0 0-4-4m4 4 4-4M5 18h14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
      <span className="max-sm:hidden">Download JSON report</span>
    </button>
  );
}
