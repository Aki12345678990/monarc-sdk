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
    <button type="button" onClick={download} className="btn-primary">
      Download report JSON
    </button>
  );
}
