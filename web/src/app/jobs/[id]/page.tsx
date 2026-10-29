import { Suspense } from "react";
import { JobView } from "@/components/JobView";

export default function JobPage({ params }: { params: Promise<{ id: string }> }) {
  return (
    <Suspense fallback={<p>Loading job…</p>}>
      {params.then(({ id }) => (
        <JobView jobId={id} />
      ))}
    </Suspense>
  );
}
