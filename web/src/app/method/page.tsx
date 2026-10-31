export default function MethodPage() {
  return (
    <article className="mx-auto max-w-[760px] space-y-4">
      <h1 className="text-3xl">Method</h1>
      <p>
        analyzer_core is a static analyzer for Android APK files. It checks the archive, reads
        package and SDK metadata, and writes a JSON report. This website is a research prototype
        from an MSc Cyber Security dissertation.
      </p>
      <p>It does not execute APK code. No code from the APK is executed.</p>
      <p>
        D and N are implemented. A is unavailable (API map not finalised). P and M are not
        implemented. The report shows raw permissions and raw manifest facts. Schema 1.1.0 adds a
        univariate corpus comparison (percentile and histogram per metric; no pairing of
        indicators).
      </p>
      <p>The UI shows indicators exactly as the report states them.</p>
      <h2 className="section-title">What this does not do</h2>
      <ul className="list-disc pl-6">
        <li>Does not combine indicators into one number.</li>
        <li>No rating.</li>
        <li>This is not a malware verdict.</li>
      </ul>
      <h2 className="section-title">Data handling</h2>
      <p>
        Uploaded APKs are deleted after analysis. Reports are kept, keyed by the file&apos;s SHA-256
        hash. Only upload apps you are permitted to analyse.
      </p>
    </article>
  );
}
