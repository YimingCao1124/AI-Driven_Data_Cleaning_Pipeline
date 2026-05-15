"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import useSWR from "swr";
import { getJob } from "@/lib/api";
import type { JobResponse } from "@/types/api";
import ProgressCard from "@/components/ProgressCard";
import { AlertTriangle, Loader2 } from "lucide-react";

export default function JobStatusPage() {
  const params = useParams<{ jobId: string }>();
  const router = useRouter();
  const jobId = Number(params.jobId);
  const validId = Number.isFinite(jobId);

  const { data, error } = useSWR<JobResponse>(
    validId ? ["job", jobId] : null,
    () => getJob(jobId),
    {
      // Stop polling once the job reaches a terminal state.
      refreshInterval: (d) =>
        d?.status === "completed" || d?.status === "failed" ? 0 : 2000,
    }
  );

  useEffect(() => {
    if (data?.status === "completed") {
      const t = setTimeout(() => router.push(`/results/${jobId}`), 600);
      return () => clearTimeout(t);
    }
  }, [data?.status, jobId, router]);

  if (!validId) {
    return (
      <div className="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
        Invalid job id. <Link href="/upload" className="underline">Start a new extraction</Link>.
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
        Failed to load job: {(error as Error).message}
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center gap-2 text-slate-500">
        <Loader2 className="h-4 w-4 animate-spin" /> Loading job…
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">Step 3 — Job running</h1>
        <p className="mt-1 text-sm text-slate-600">
          The page polls every 2 seconds. When the job completes you&apos;ll be
          redirected to the results.
        </p>
      </header>
      <ProgressCard job={data} />
      {data.status === "completed" && (
        <p className="text-sm text-slate-500">
          Redirecting to{" "}
          <Link className="text-brand-600 underline" href={`/results/${jobId}`}>
            results
          </Link>
          …
        </p>
      )}
      {data.status === "failed" && (
        <div className="flex items-start gap-3 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <AlertTriangle className="mt-0.5 h-5 w-5 flex-none" />
          <div>
            <p className="font-semibold">The job did not complete.</p>
            <p className="mt-1">
              You can still inspect any partial results, or start over from{" "}
              <Link href="/upload" className="underline">
                /upload
              </Link>
              .
            </p>
            <Link
              href={`/results/${jobId}`}
              className="mt-3 inline-block rounded border border-red-300 bg-white px-3 py-1.5 text-red-700 hover:bg-red-100"
            >
              View partial results
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
