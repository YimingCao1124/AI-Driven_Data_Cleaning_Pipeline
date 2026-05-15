"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import useSWR from "swr";
import {
  exportUrl,
  getJob,
  getJobResults,
  getTemplate,
  retryFailed,
} from "@/lib/api";
import type {
  JobResponse,
  ResultResponse,
  TemplateResponse,
} from "@/types/api";
import EditResultDialog from "@/components/EditResultDialog";
import { Download, Loader2, Pencil, RefreshCw } from "lucide-react";

type Filter = "all" | "success" | "failed";

export default function ResultsPage() {
  const params = useParams<{ jobId: string }>();
  const jobId = Number(params.jobId);

  const [filter, setFilter] = useState<Filter>("all");
  const [editing, setEditing] = useState<ResultResponse | null>(null);
  const [retrying, setRetrying] = useState(false);

  const { data: job, mutate: refetchJob } = useSWR<JobResponse>(
    Number.isFinite(jobId) ? ["job-summary", jobId] : null,
    () => getJob(jobId),
    { refreshInterval: 4000 }
  );

  const { data: template } = useSWR<TemplateResponse>(
    job ? ["template", job.template_id] : null,
    () => getTemplate(job!.template_id)
  );

  const {
    data: results,
    mutate: refetchResults,
  } = useSWR<ResultResponse[]>(
    Number.isFinite(jobId) ? ["results", jobId, filter] : null,
    () => getJobResults(jobId, filter),
    { refreshInterval: 4000 }
  );

  useEffect(() => {
    if (job?.status === "completed") {
      refetchResults();
    }
  }, [job?.status, refetchResults]);

  const fieldNames = useMemo(
    () => (template?.fields ?? []).map((f) => f.name),
    [template]
  );

  async function handleRetry() {
    setRetrying(true);
    try {
      await retryFailed(jobId);
      // poll a couple of times for the retry thread to finish
      await new Promise((r) => setTimeout(r, 1500));
      await Promise.all([refetchJob(), refetchResults()]);
    } finally {
      setRetrying(false);
    }
  }

  if (!job) {
    return (
      <div className="flex items-center gap-2 text-slate-500">
        <Loader2 className="h-4 w-4 animate-spin" /> Loading…
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Step 4 — Review &amp; export
          </h1>
          <p className="text-sm text-slate-600">
            Job #{job.id} · {job.success_count}/{job.total_count} success ·{" "}
            {job.failed_count} failed
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleRetry}
            disabled={retrying || job.failed_count === 0}
            className="btn-secondary"
          >
            {retrying ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
            Retry failed
          </button>
          <a className="btn-secondary" href={exportUrl(jobId, "csv")}>
            <Download className="mr-2 h-4 w-4" /> CSV
          </a>
          <a className="btn-primary" href={exportUrl(jobId, "xlsx")}>
            <Download className="mr-2 h-4 w-4" /> XLSX
          </a>
        </div>
      </header>

      <div className="flex gap-2">
        {(["all", "success", "failed"] as Filter[]).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={
              filter === f
                ? "btn-primary"
                : "btn-secondary"
            }
          >
            {f === "all" ? "All" : f === "success" ? "Success" : "Failed"}
          </button>
        ))}
      </div>

      <div className="overflow-x-auto rounded-md border bg-white">
        <table className="data-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Input text</th>
              {fieldNames.map((name) => (
                <th key={name}>{name}</th>
              ))}
              <th>Status</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {(results ?? []).map((r) => (
              <tr key={r.id}>
                <td className="text-slate-500">{r.source_row_index + 1}</td>
                <td className="max-w-[320px] whitespace-pre-wrap break-words text-slate-700">
                  {r.input_text}
                </td>
                {fieldNames.map((name) => {
                  const v = r.output[name];
                  let display: string;
                  if (v === null || v === undefined || v === "") display = "—";
                  else if (typeof v === "boolean") display = v ? "true" : "false";
                  else display = String(v);
                  return (
                    <td key={name} className="text-slate-800">
                      {display}
                    </td>
                  );
                })}
                <td>
                  <span
                    className={r.status === "success" ? "badge-success" : "badge-failed"}
                    title={
                      r.status === "failed"
                        ? r.validation_errors.map((e) => e.msg).join("; ")
                        : ""
                    }
                  >
                    {r.status}
                  </span>
                </td>
                <td>
                  <button
                    onClick={() => setEditing(r)}
                    className="rounded p-1 text-slate-500 hover:bg-slate-100"
                  >
                    <Pencil className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
            {(!results || results.length === 0) && (
              <tr>
                <td colSpan={fieldNames.length + 4} className="py-8 text-center text-slate-400">
                  {job.status === "running" ? "Job still running…" : "No results."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <EditResultDialog
        result={editing}
        template={template ?? null}
        onClose={() => setEditing(null)}
        onSaved={() => refetchResults()}
      />
    </div>
  );
}
