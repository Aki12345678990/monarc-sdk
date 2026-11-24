import headlines from "@/lib/paper-headlines.json";
import { EXPOSURE_DISCLAIMER } from "@/lib/exposure-copy";

const ORDER = ["H01", "H02", "H03", "H04", "H06"] as const;

export default function MethodPage() {
  return (
    <article className="mx-auto max-w-[760px] space-y-4">
      <h1 className="text-3xl">Method</h1>
      <p>
        analyzer_core measures an Android APK the same way as the frozen research pipeline. It does
        not execute APK code.
      </p>
      <h2 className="section-title">Indicators</h2>
      <ul className="list-disc pl-6">
        <li>P: distinct dangerous permissions declared with uses-permission or uses-permission-sdk-23, excluding a declaration whose maxSdkVersion is below minSdkVersion.</li>
        <li>A: distinct sensitive API pairs from the 242-entry map, called from SDK-attributed code.</li>
        <li>N: distinct network hosts referenced in SDK code.</li>
        <li>D: third-party SDK footprint, the share of packages attributed to an SDK.</li>
        <li>M: exported components that are unprotected and are not the launcher. M_exp_sdk counts only classes in SDK namespaces. debuggable, allowBackup and cleartext are reported as separate facts.</li>
      </ul>
      <h2 className="section-title">Exposure index</h2>
      <p>R = ¼·pr(P) + ¼·pr(A) + ¼·pr(N) + ¼·pr(D)</p>
      <p>R₋D = ⅓·pr(P) + ⅓·pr(A) + ⅓·pr(N)</p>
      <p>
        pr(x) = {headlines.percentile_formula}, where L is the number of corpus values below x, E is
        the number equal to x, and n is {headlines.n_apps}. {headlines.percentile_note}
      </p>
      <p>{EXPOSURE_DISCLAIMER}</p>
      <h2 className="section-title">Paper results</h2>
      <p>Primary partial Spearman correlation of D with each outcome, 95% interval, on the {headlines.n_apps} included apps.</p>
      <table className="data-table">
        <caption className="sr-only">Partial Spearman results</caption>
        <thead>
          <tr>
            <th scope="col">Hypothesis</th>
            <th scope="col">Outcome</th>
            <th scope="col">rho</th>
            <th scope="col">95% interval</th>
            <th scope="col">Significant</th>
          </tr>
        </thead>
        <tbody>
          {ORDER.map((id) => {
            const row = headlines.hypotheses[id];
            return (
              <tr key={id}>
                <td>{id}</td>
                <td>{row.outcome}</td>
                <td>{row.rho_p.toFixed(3)}</td>
                <td>
                  {row.ci95_low.toFixed(3)} to {row.ci95_high.toFixed(3)}
                </td>
                <td>{row.significant ? "yes" : "no"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      {headlines.parity ? <p>{headlines.parity}</p> : null}
      <h2 className="section-title">What this does not do</h2>
      <ul className="list-disc pl-6">
        <li>This is not a malware verdict.</li>
      </ul>
    </article>
  );
}
