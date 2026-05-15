"use client";

import { useEffect, useState } from "react";
import type { ResultResponse, TemplateResponse, FieldDefinition } from "@/types/api";
import { updateResult } from "@/lib/api";
import { Loader2, X } from "lucide-react";

interface Props {
  result: ResultResponse | null;
  template: TemplateResponse | null;
  onClose: () => void;
  onSaved: (updated: ResultResponse) => void;
}

export default function EditResultDialog({ result, template, onClose, onSaved }: Props) {
  const [values, setValues] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!result) return;
    const initial: Record<string, string> = {};
    for (const f of template?.fields ?? []) {
      const v = result.output[f.name];
      if (v === null || v === undefined) {
        initial[f.name] = "";
      } else if (typeof v === "boolean") {
        initial[f.name] = v ? "true" : "false";
      } else {
        initial[f.name] = String(v);
      }
    }
    setValues(initial);
    setError(null);
  }, [result, template]);

  if (!result || !template) return null;

  async function handleSave() {
    if (!result) return;
    setSaving(true);
    setError(null);
    try {
      const output: Record<string, unknown> = {};
      for (const f of template?.fields ?? []) {
        const raw = values[f.name];
        if (raw === "" || raw === undefined) {
          output[f.name] = null;
          continue;
        }
        output[f.name] = coerce(f, raw);
      }
      const updated = await updateResult(result.id, output);
      onSaved(updated);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4">
      <div className="w-full max-w-2xl rounded-lg bg-white shadow-xl">
        <div className="flex items-center justify-between border-b px-5 py-3">
          <h2 className="font-semibold text-slate-800">Edit result #{result.id}</h2>
          <button onClick={onClose} className="rounded p-1 hover:bg-slate-100">
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="space-y-4 p-5">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Source input
            </p>
            <p className="mt-1 whitespace-pre-wrap rounded-md border bg-slate-50 p-3 text-sm text-slate-700">
              {result.input_text}
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {(template?.fields ?? []).map((f) => (
              <div key={f.name}>
                <label className="block text-sm font-medium text-slate-700">
                  {f.name}{" "}
                  <span className="text-xs font-normal text-slate-400">({f.type})</span>
                </label>
                {f.type === "boolean" ? (
                  <select
                    className="select"
                    value={values[f.name] ?? ""}
                    onChange={(e) => setValues((v) => ({ ...v, [f.name]: e.target.value }))}
                  >
                    <option value="">—</option>
                    <option value="true">true</option>
                    <option value="false">false</option>
                  </select>
                ) : (
                  <input
                    className="input"
                    value={values[f.name] ?? ""}
                    onChange={(e) => setValues((v) => ({ ...v, [f.name]: e.target.value }))}
                  />
                )}
              </div>
            ))}
          </div>
          {error && (
            <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          )}
        </div>
        <div className="flex justify-end gap-2 border-t bg-slate-50 px-5 py-3">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button onClick={handleSave} disabled={saving} className="btn-primary">
            {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

function coerce(field: FieldDefinition, raw: string): unknown {
  switch (field.type) {
    case "boolean":
      return raw === "true";
    case "integer":
      return Number.parseInt(raw, 10);
    case "float":
      return Number.parseFloat(raw);
    default:
      return raw;
  }
}
