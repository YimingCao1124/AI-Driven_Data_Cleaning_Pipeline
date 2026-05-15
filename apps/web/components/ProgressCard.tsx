import type { JobResponse } from "@/types/api";

export default function ProgressCard({ job }: { job: JobResponse }) {
  return (
    <div className="card space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Job #{job.id}</h2>
          <p className="text-sm text-slate-500">
            Status: <StatusBadge status={job.status} />
          </p>
        </div>
        <div className="text-3xl font-bold text-brand-600">{job.progress_percent}%</div>
      </div>

      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200">
        <div
          className="h-full bg-brand-600 transition-all"
          style={{ width: `${job.progress_percent}%` }}
        />
      </div>

      <div className="grid grid-cols-4 gap-3">
        <Counter label="Total" value={job.total_count} />
        <Counter label="Processed" value={job.processed_count} />
        <Counter label="Success" value={job.success_count} accent="text-emerald-600" />
        <Counter label="Failed" value={job.failed_count} accent="text-red-600" />
      </div>
    </div>
  );
}

function Counter({
  label,
  value,
  accent,
}: {
  label: string;
  value: number;
  accent?: string;
}) {
  return (
    <div className="rounded-md border bg-slate-50 px-3 py-2">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className={`text-lg font-semibold ${accent ?? "text-slate-800"}`}>{value}</div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const cls =
    status === "completed"
      ? "badge-success"
      : status === "failed"
      ? "badge-failed"
      : status === "running"
      ? "badge-running"
      : "badge-pending";
  return <span className={cls}>{status}</span>;
}
