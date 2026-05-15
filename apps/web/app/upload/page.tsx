"use client";

import Link from "next/link";
import { useState } from "react";
import { uploadFile } from "@/lib/api";
import type { FileUploadResponse } from "@/types/api";
import FilePreview from "@/components/FilePreview";
import { ArrowRight, FileUp, Loader2 } from "lucide-react";

export default function UploadPage() {
  const [file, setFile] = useState<FileUploadResponse | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const input = e.target;
    const f = input.files?.[0];
    if (!f) return;
    setUploading(true);
    setError(null);
    setFile(null);
    try {
      const resp = await uploadFile(f);
      setFile(resp);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setUploading(false);
      // Reset so re-selecting the same file fires onChange again.
      input.value = "";
    }
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">Step 1 — Upload your file</h1>
        <p className="mt-1 text-slate-600">
          Accepted formats: <code>.xlsx</code>, <code>.csv</code>. Max 25 MB.
        </p>
      </header>

      <div className="card">
        <label
          htmlFor="file-input"
          className="flex flex-col items-center justify-center gap-3 rounded-md border-2 border-dashed border-slate-300 bg-slate-50 p-10 text-center hover:bg-slate-100 cursor-pointer"
        >
          {uploading ? (
            <Loader2 className="h-8 w-8 animate-spin text-brand-600" />
          ) : (
            <FileUp className="h-8 w-8 text-slate-400" />
          )}
          <div>
            <p className="font-medium text-slate-700">
              {uploading ? "Uploading…" : "Click to choose a file"}
            </p>
            <p className="text-xs text-slate-500">
              Or try the bundled sample{" "}
              <code className="rounded bg-white px-1 py-0.5 text-[11px]">
                examples/education_experience_sample.csv
              </code>
            </p>
          </div>
          <input
            id="file-input"
            type="file"
            className="hidden"
            accept=".xlsx,.csv"
            onChange={handleFileChange}
            disabled={uploading}
          />
        </label>
      </div>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {file && (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">
                Preview — {file.filename}
              </h2>
              <p className="text-sm text-slate-500">
                {file.total_rows} rows total · showing first {file.preview_rows.length}
              </p>
            </div>
            <Link href={`/run?file_id=${file.file_id}`} className="btn-primary">
              Continue <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </div>
          <FilePreview file={file} />
        </section>
      )}
    </div>
  );
}
