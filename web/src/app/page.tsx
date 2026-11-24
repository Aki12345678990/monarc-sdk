import { RecentAnalyses, UploadForm } from "@/components/UploadForm";

export default function Home() {
  return (
    <div className="landing-bento">
      <section aria-labelledby="intro-heading" className="card span-7">
        <h1 id="intro-heading" className="hero-title chrome-text">
          See what the SDKs inside an app bring with them
        </h1>
        <p className="mt-3 text-muted">
          This is a research prototype from an MSc Cyber Security dissertation. It performs static
          analysis of an Android APK and reports its third-party SDK footprint and attack-surface
          facts. No code from the APK is executed.
        </p>
      </section>

      <section aria-labelledby="upload-heading" className="span-5">
        <h2 id="upload-heading" className="section-title mb-2">
          Upload an APK
        </h2>
        <UploadForm />
      </section>

      <div className="span-12 landing-cards">
        <section className="card">
          <h2 className="section-title">P</h2>
          <p className="mt-2">Distinct dangerous permissions declared by the app.</p>
        </section>
        <section className="card">
          <h2 className="section-title">A</h2>
          <p className="mt-2">Distinct sensitive APIs called from SDK code.</p>
        </section>
        <section className="card">
          <h2 className="section-title">N</h2>
          <p className="mt-2">Distinct network hosts referenced in SDK code (indicator N).</p>
        </section>
        <section className="card">
          <h2 className="section-title">D</h2>
          <p className="mt-2">Third-party SDK footprint from package namespaces (indicator D).</p>
        </section>
        <section className="card">
          <h2 className="section-title">M</h2>
          <p className="mt-2">Exported components in SDK code, with manifest flags listed separately.</p>
        </section>
        <section className="card">
          <h2 className="section-title">Exposure index</h2>
          <p className="mt-2">Ordinal ranking of P, A, N and D against the research corpus.</p>
        </section>
        <section aria-labelledby="not-heading" className="card">
          <h2 id="not-heading" className="section-title">
            What it does not do
          </h2>
          <ul className="mt-2 list-disc pl-6">
            <li>This is not a malware verdict.</li>
          </ul>
        </section>
      </div>

      <section aria-labelledby="data-heading" className="card span-12">
        <h2 id="data-heading" className="section-title">
          Data handling
        </h2>
        <p className="mt-2">
          Uploaded APKs are deleted after analysis. Reports are kept, keyed by the file&apos;s
          SHA-256 hash.
        </p>
        <p className="mt-2 font-semibold">Only upload apps you are permitted to analyse.</p>
      </section>

      <RecentAnalyses />
    </div>
  );
}
