import { UploadForm } from "@/components/UploadForm";

export default function Home() {
  return (
    <div className="space-y-6">
      <section aria-labelledby="intro-heading" className="space-y-3">
        <h1 id="intro-heading" className="text-4xl">
          Analyse an Android APK
        </h1>
        <p>
          This is a research prototype from an MSc Cyber Security dissertation. It performs static
          analysis of an Android APK and reports its third-party SDK footprint and attack-surface
          facts. No code from the APK is executed.
        </p>
      </section>

      <section aria-labelledby="not-heading" className="card">
        <h2 id="not-heading" className="text-2xl">
          What this does not do
        </h2>
        <ul className="mt-2 list-disc pl-6">
          <li>No risk score.</li>
          <li>No rating.</li>
          <li>No malware verdict.</li>
        </ul>
      </section>

      <section aria-labelledby="data-heading" className="card">
        <h2 id="data-heading" className="text-2xl">
          Data handling
        </h2>
        <p className="mt-2">
          Uploaded APKs are deleted after analysis. Reports are kept, keyed by the file&apos;s
          SHA-256 hash.
        </p>
        <p className="mt-2 font-semibold">Only upload apps you are permitted to analyse.</p>
      </section>

      <UploadForm />
    </div>
  );
}
