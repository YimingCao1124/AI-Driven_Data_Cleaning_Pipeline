"use client";

import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import useSWR from "swr";
import { getJob } from "@/lib/api";
import type { JobResponse } from "@/types/api";
import ProgressCard from "@/components/ProgressCard";
import { Loader2 } from "lucide-react";

export default function JobStatusPage() {
  const params = useParams<{ jobId: string }>();
  const router = useRouter();
  const jobId = Number(params.jobId);

  const { data, error } = useSWR<JobResponse>(
    Number.isFinite(jobId) ? ["job", jobId] : null,
    () => getJob(jobId),
    { refreshInterval: 2000 }
  );

  useEffect(() => {
    if (data?.status === "completed") {
      const t = setTimeout(() => router.push(`/results/${jobId}`), 600);
      return () => clearTimeout(t);
    }
  }, [data?.status, jobId, router]);

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
          Redirecting to <a className="text-brand-600 underline" href={`/results/${jobId}`}>results</a>…
        </p>
      )}
    </div>
  );
}
