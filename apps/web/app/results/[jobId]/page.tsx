"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
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

type Filter = "all" | "success" | "failed" | "archived";

const TERMINAL_STATES: ReadonlyArray<JobResponse["status"]> = ["completed", "failed"];

export default function ResultsPage() {
  const params = useParams<{ jobId: string }>();
  const jobId = Number(params.jobId);
  const validId = Number.isFinite(jobId);

  const [filter, setFilter] = useState<Filter>("all");
  const [editing, setEditing] = useState<ResultResponse | null>(null);
  const [retrying, setRetrying] = useState(false);

  const { data: job, mutate: refetchJob } = useSWR<JobResponse>(
    validId ? ["job-summary", jobId] : null,
    () => getJob(jobId),
    {
      refreshInterval: (d) => (d && TERMINAL_STATES.includes(d.status) ? 0 : 4000),
    }
  );

  const { data: template } = useSWR<TemplateResponse>(
    job ? ["template", job.template_id] : null,
    () => getTemplate(job!.template_id)
  );

  const {
    data: results,
    mutate: refetchResults,
  } = useSWR<ResultResponse[]>(
    validId ? ["results", jobId, filter] : null,
    () => getJobResults(jobId, filter),
    {
      refreshInterval: () =>
        job && TERMINAL_STATES.includes(job.status) ? 0 : 4000,
    }
  );

  useEffect(() => {
    if (job && TERMINAL_STATES.includes(job.status)) {
      refetchResults();
    }
  }, [job, refetchResults]);

  const fieldNames = useMemo(
    () => (template?.fields ?? []).map((f) => f.name),
    [template]
  );

  async function handleRetry() {
    setRetrying(true);
    try {
      await retryFailed(jobId);
      // Switch to "all" so newly-succeeded rows are visible to the user.
      setFilter("all");
      // Poll the job until it leaves the running state (or up to ~30 s).
      for (let i = 0; i < 60; i++) {
        await new Promise((r) => setTimeout(r, 500));
        const next = await refetchJob();
        if (next && TERMINAL_STATES.includes(next.status)) break;
      }
      await refetchResults();
    } finally {
      setRetrying(false);
    }
  }

  if (!validId) {
    return (
      <div className="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
        Invalid job id.{" "}
        <Link href="/upload" className="underline">
          Start a new extraction
        </Link>
        .
      </div>
    );
  }

  if (!job) {
    return (
      <div className="flex items-center gap-2 text-slate-500">
        <Loader2 className="h-4 w-4 animate-spin" /> Loading…
      </div>
    );
  }

  const columnCount = fieldNames.length + 4;

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Step 4 — Review &amp; export
          </h1>
          <p className="text-sm text-slate-600">
            Job #{job.id} · {job.success_count}/{job.total_count} success ·{" "}
            {job.failed_count} failed · {job.archived_count} archived
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleRetry}
            disabled={retrying || job.failed_count === 0}
            title={job.failed_count === 0 ? "No failed rows to retry" : ""}
            className="btn-secondary"
          >
            {retrying ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="mr-2 h-4 w-4" />
            )}
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

      <div className="flex flex-wrap gap-2">
        {(["all", "success", "failed", "archived"] as Filter[]).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={filter === f ? "btn-primary" : "btn-secondary"}
          >
            {f === "all"
              ? `All (${job.processed_count})`
              : f === "success"
              ? `Success (${job.success_count})`
              : f === "failed"
              ? `Failed (${job.failed_count})`
              : `Archived (${job.archived_count})`}
          </button>
        ))}
      </div>

      <div className="overflow-x-auto rounded-md border bg-white">
        <table className="data-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Input text</th>
              {fieldNames.map((name, idx) => (
                <th key={idx}>{name}</th>
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
                {fieldNames.map((name, idx) => {
                  const v = r.output[name];
                  let display: string;
                  if (v === null || v === undefined || v === "") display = "—";
                  else if (typeof v === "boolean") display = v ? "true" : "false";
                  else display = String(v);
                  return (
                    <td key={idx} className="text-slate-800">
                      {display}
                    </td>
                  );
                })}
                <td>
                  <span
                    className={
                      r.status === "success"
                        ? "badge-success"
                        : r.status === "archived"
                        ? "badge-archived"
                        : "badge-failed"
                    }
                    title={
                      r.status !== "success"
                        ? r.validation_errors
                            .map((e) => e.msg ?? JSON.stringify(e))
                            .join("; ")
                        : ""
                    }
                  >
                    {r.status}
                  </span>
                </td>
                <td>
                  <button
                    onClick={() => setEditing(r)}
                    aria-label="Edit result"
                    className="rounded p-1 text-slate-500 hover:bg-slate-100"
                  >
                    <Pencil className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
            {(!results || results.length === 0) && (
              <tr>
                <td
                  colSpan={columnCount}
                  className="py-8 text-center text-slate-400"
                >
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
