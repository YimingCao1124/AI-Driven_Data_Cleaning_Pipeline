"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { createJob, getFile, listTemplates } from "@/lib/api";
import type { FileUploadResponse, TemplateResponse } from "@/types/api";
import { Play, Loader2 } from "lucide-react";

export default function RunPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center gap-2 text-slate-500">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading…
        </div>
      }
    >
      <RunPageInner />
    </Suspense>
  );
}

function RunPageInner() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const fileIdParam = searchParams.get("file_id");
  const fileId = fileIdParam ? Number(fileIdParam) : null;

  const [file, setFile] = useState<FileUploadResponse | null>(null);
  const [templates, setTemplates] = useState<TemplateResponse[]>([]);
  const [templateId, setTemplateId] = useState<number | null>(null);
  const [inputColumn, setInputColumn] = useState<string>("");
  const [maxRows, setMaxRows] = useState<number>(100);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!fileId) return;
    let cancelled = false;
    (async () => {
      try {
        const [f, tpls] = await Promise.all([getFile(fileId), listTemplates()]);
        if (cancelled) return;
        setFile(f);
        setTemplates(tpls);
        if (tpls.length) setTemplateId(tpls[0].id);
        if (f.headers.length) {
          // Prefer a column likely to hold free-text. Otherwise default to the
          // last column (the original internship script's "experience" column
          // is the last one in the bundled sample).
          const preferred =
            f.headers.find((h) => h.toLowerCase().includes("experience")) ??
            f.headers[f.headers.length - 1];
          setInputColumn(preferred);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [fileId]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!fileId || !templateId || !inputColumn) return;
    setSubmitting(true);
    setError(null);
    try {
      const job = await createJob({
        file_id: fileId,
        template_id: templateId,
        input_column: inputColumn,
        max_rows: maxRows,
      });
      router.push(`/jobs/${job.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setSubmitting(false);
    }
  }

  if (!fileId) {
    return (
      <div className="card">
        <p className="text-slate-600">
          No file selected. Please <a href="/upload" className="text-brand-600 underline">upload a file</a> first.
        </p>
      </div>
    );
  }

  if (!file) {
    return (
      <div className="flex items-center gap-2 text-slate-500">
        <Loader2 className="h-4 w-4 animate-spin" /> Loading file…
      </div>
    );
  }

  const selectedTemplate = templates.find((t) => t.id === templateId);

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <form className="card space-y-5 lg:col-span-2" onSubmit={handleSubmit}>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Step 2 — Configure extraction</h1>
          <p className="mt-1 text-sm text-slate-600">
            File: <strong>{file.filename}</strong> · {file.total_rows} rows
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">Input column</label>
          <p className="mb-1 text-xs text-slate-500">
            Which column should be fed into the extractor as free-form text?
          </p>
          <select
            className="select"
            value={inputColumn}
            onChange={(e) => setInputColumn(e.target.value)}
          >
            {file.headers.map((h) => (
              <option key={h} value={h}>
                {h}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">Template</label>
          <select
            className="select"
            value={templateId ?? ""}
            onChange={(e) => setTemplateId(Number(e.target.value))}
          >
            {templates.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name} {t.is_builtin ? "(built-in)" : ""}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">
            Max rows
          </label>
          <p className="mb-1 text-xs text-slate-500">
            Cap the number of rows processed (1–10000). Lower this for a fast first run.
          </p>
          <input
            type="number"
            className="input"
            min={1}
            max={10000}
            value={maxRows}
            onChange={(e) => setMaxRows(Number(e.target.value))}
          />
        </div>

        {error && (
          <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <button type="submit" disabled={submitting || !templateId} className="btn-primary">
          {submitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
          Run Extraction
        </button>
      </form>

      <aside className="card">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Template fields
        </h2>
        {selectedTemplate ? (
          <ul className="space-y-2 text-sm">
            {selectedTemplate.fields.map((f) => (
              <li key={f.name}>
                <div className="flex items-center gap-2">
                  <code className="font-mono text-slate-800">{f.name}</code>
                  <span className="text-xs text-slate-500">{f.type}</span>
                  {f.required && (
                    <span className="rounded-full bg-red-100 px-1.5 py-0.5 text-[10px] text-red-700">
                      required
                    </span>
                  )}
                </div>
                {f.description && (
                  <p className="text-xs text-slate-500">{f.description}</p>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-500">No template selected.</p>
        )}
      </aside>
    </div>
  );
}
