import Link from "next/link";
import { ArrowRight, FileSpreadsheet, ListChecks, Wand2, Download } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="space-y-12">
      <section className="grid gap-8 lg:grid-cols-2 lg:items-center">
        <div>
          <div className="mb-3 inline-flex items-center rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-700">
            Version 1 — MVP
          </div>
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
            Turn messy spreadsheet text into clean structured tables.
          </h1>
          <p className="mt-4 text-lg text-slate-600">
            AI Data Extraction Studio is a schema-driven, full-stack AI data cleaning
            tool. Upload an Excel or CSV, pick a column of free-form text, and let the
            built-in <em>Education Experience Cleaner</em> extract structured fields
            — all running locally with a mock LLM. No API keys required.
          </p>
          <div className="mt-6 flex gap-3">
            <Link href="/upload" className="btn-primary">
              Start Extraction <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </div>
          <p className="mt-3 text-xs text-slate-500">
            Bundled sample file:{" "}
            <code className="rounded bg-slate-100 px-1 py-0.5">
              examples/education_experience_sample.csv
            </code>
          </p>
        </div>

        <div className="card">
          <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
            Workflow
          </h2>
          <ol className="space-y-3 text-sm">
            <Step icon={<FileSpreadsheet className="h-4 w-4" />} title="1. Upload Excel / CSV">
              Drop in a file containing a column of messy natural-language text.
            </Step>
            <Step icon={<ListChecks className="h-4 w-4" />} title="2. Pick the input column">
              Choose which column to feed into the extractor.
            </Step>
            <Step icon={<Wand2 className="h-4 w-4" />} title="3. Run the AI extraction">
              The mock LLM processes each row, validates against the schema, and
              automatically retries failures.
            </Step>
            <Step icon={<ListChecks className="h-4 w-4" />} title="4. Review &amp; edit">
              Filter success/failed, inline-edit any field, retry failed rows.
            </Step>
            <Step icon={<Download className="h-4 w-4" />} title="5. Export CSV / XLSX">
              Original columns are preserved; extracted fields are appended.
            </Step>
          </ol>
        </div>
      </section>

      <section className="card border-amber-200 bg-amber-50">
        <h2 className="mb-2 font-semibold text-amber-900">About this V1</h2>
        <p className="text-sm text-amber-900/80">
          V1 covers a single use case end-to-end: row-wise extraction from Excel/CSV
          with one built-in template (<em>Education Experience Cleaner</em>) and a
          mock LLM. Custom schemas, real LLM providers, DOCX/PDF, OCR, and team
          features are planned for V2–V6 — see the README Roadmap.
        </p>
      </section>
    </div>
  );
}

function Step({
  icon,
  title,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <li className="flex gap-3">
      <span className="mt-0.5 flex h-6 w-6 flex-none items-center justify-center rounded-full bg-brand-100 text-brand-700">
        {icon}
      </span>
      <span>
        <strong className="block text-slate-800">{title}</strong>
        <span className="text-slate-600">{children}</span>
      </span>
    </li>
  );
}
