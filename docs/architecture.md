# Architecture Overview (V1)

This document describes how the V1 MVP fits together internally and where future extension points live.

---

## High-level diagram

```
┌──────────────────────────┐      HTTP/JSON        ┌──────────────────────────────────┐
│  Next.js 14 Frontend     │ ────────────────────► │  FastAPI Backend                 │
│                          │ ◄──────────────────── │                                  │
│  TypeScript + Tailwind   │                       │  ┌────────────────────────────┐  │
│  shadcn/ui               │                       │  │ Routers                    │  │
│  TanStack Table          │                       │  │  /files /templates /jobs   │  │
│                          │                       │  │  /results /export /health  │  │
│  Pages:                  │                       │  └─────────────┬──────────────┘  │
│   /  /upload  /run       │                       │                ▼                 │
│   /jobs/[id]             │                       │  ┌────────────────────────────┐  │
│   /results/[id]          │                       │  │ Service layer              │  │
│                          │                       │  │  excel_parser              │  │
└──────────────────────────┘                       │  │  prompt_builder            │  │
                                                   │  │  llm_client (Mock + ABC)   │  │
                                                   │  │  validator (Pydantic)      │  │
                                                   │  │  extractor (retry loop)    │  │
                                                   │  │  job_runner (threaded)     │  │
                                                   │  │  exporter (CSV/XLSX)       │  │
                                                   │  └─────────────┬──────────────┘  │
                                                   │                ▼                 │
                                                   │  ┌────────────────────────────┐  │
                                                   │  │ SQLite (SQLAlchemy 2.x)    │  │
                                                   │  │  uploaded_files            │  │
                                                   │  │  extraction_templates      │  │
                                                   │  │  extraction_jobs           │  │
                                                   │  │  extraction_results        │  │
                                                   │  └────────────────────────────┘  │
                                                   └──────────────────────────────────┘
```

---

## Data flow — one extraction run

1. **Upload** — The user uploads an `.xlsx` or `.csv` file. The backend saves it under `storage/uploads/<uuid>__<original_name>`, parses headers + a 20-row preview + the total row count, and stores a row in `uploaded_files`.

2. **Run** — The user selects a column from that file, picks a template (V1 ships one: *Education Experience Cleaner*), and submits a `POST /api/jobs`. The backend creates an `extraction_jobs` row in status `pending` and starts a daemon thread that runs the job.

3. **Job execution** — The job runner reads the file from disk, takes the rows up to `max_rows`, and uses a `ThreadPoolExecutor(max_workers=MAX_CONCURRENCY)` to process rows concurrently. For each row:

   a. `prompt_builder` builds a structured prompt from the template's instruction, field schema, and examples, and embeds the input text from the chosen column.

   b. `llm_client.extract(prompt)` calls the configured client. In V1 the only real implementation is `MockLLMClient`, which performs regex- and keyword-based extraction so the demo "just works" without any API keys.

   c. `validator.validate_output(raw_text, model_cls)` strips any code fences, parses the JSON, and runs it through a dynamic Pydantic model built from the template's `fields_json`.

   d. If validation fails, the loop builds a retry prompt that includes the error feedback and asks the model to correct itself. This repeats up to `MAX_RETRIES`.

   e. The result is written to `extraction_results` with `status = success | failed`, raw model output, validation errors (if any), and retry count.

   f. The job's `processed_count` / `success_count` / `failed_count` are incremented atomically. When all rows are done the job is marked `completed`.

4. **Review** — The frontend polls `GET /api/jobs/{id}` every 2 seconds until the job is `completed`, then loads `GET /api/jobs/{id}/results`. The user can filter by status, click any row to open an edit dialog, and `PATCH /api/results/{id}` to save manual fixes.

5. **Export** — `GET /api/jobs/{id}/export?format=csv|xlsx` rebuilds a DataFrame from the original file's columns + the extracted fields appended, and streams the file back.

---

## Module responsibilities

| Module | Role | Future extension point |
|---|---|---|
| `services/excel_parser.py` | Parse `.xlsx` and `.csv` into headers + rows + preview | V4 will add `services/document_parser.py` for `.docx`, `.pdf`, `.txt`, `.md` |
| `services/prompt_builder.py` | Render a template + input into a single LLM prompt | V2 will accept user-defined instructions/fields/examples |
| `services/llm_client.py` | Abstract LLM provider; only `MockLLMClient` in V1 | V3 will add `OpenAIClient`, `AnthropicClient`, `DeepSeekClient` behind the same `BaseLLMClient` ABC |
| `services/validator.py` | Build a dynamic Pydantic model from a field schema; validate raw LLM output | Already generic — used unchanged for V2 custom schemas |
| `services/extractor.py` | The retry loop: prompt → call → validate → retry-with-feedback | V3 will add token/cost accounting |
| `services/job_runner.py` | Background-thread job executor with progress reporting | V6 will swap this for a Celery/Redis worker |
| `services/exporter.py` | Produce CSV/XLSX with extracted columns appended | V4 will add document-wise records exporters |
| `services/builtin_templates.py` | Hold the seed templates (1 in V1) | V2 will read user templates from DB |

---

## Database schema (V1)

```
uploaded_files
├── id (PK)
├── filename
├── file_type            ("xlsx" | "csv")
├── original_path        (absolute path under storage/uploads/)
├── headers_json         (JSON array of column names)
├── preview_rows_json    (first 20 rows as JSON array of objects)
├── total_rows
└── created_at

extraction_templates
├── id (PK)
├── name
├── description
├── extraction_mode      ("row-wise" — only mode in V1)
├── instruction          (system-style instruction text)
├── fields_json          (JSON array of FieldDef)
├── examples_json        (JSON array of in/out examples)
├── is_builtin           (boolean)
├── created_at
└── updated_at

extraction_jobs
├── id (PK)
├── file_id (FK → uploaded_files)
├── template_id (FK → extraction_templates)
├── input_column         (which column to feed into the LLM)
├── max_rows
├── status               ("pending" | "running" | "completed" | "failed")
├── total_count
├── processed_count
├── success_count
├── failed_count
├── created_at
└── updated_at

extraction_results
├── id (PK)
├── job_id (FK → extraction_jobs)
├── source_row_index
├── input_text
├── output_json          (validated, structured extraction)
├── raw_model_output     (the literal LLM response — useful for debugging)
├── validation_status    ("ok" | "invalid_json" | "schema_error")
├── validation_errors_json
├── retry_count
├── status               ("success" | "failed")
├── created_at
└── updated_at
```

`ParsedTextBlock` is intentionally **not** in V1 — it will be introduced in V4 when document-wise extraction is added.

---

## Extension points for later versions

- **V2 custom schema builder** — the `extraction_templates` table already stores `fields_json` and `examples_json` as JSON, and the validator builds Pydantic models dynamically. The only missing piece is the UI and the `POST/PATCH/DELETE /api/templates` endpoints, which are easy to add.
- **V3 real LLM providers** — implement `OpenAIClient` and `AnthropicClient` subclasses of `BaseLLMClient` and register them in the `get_llm_client(config)` factory.
- **V4 document parsing** — add a `services/document_parser.py` dispatcher, a `parsed_text_blocks` table, and a `document-wise` branch in `job_runner`.
- **V5 OCR** — wrap a Tesseract or paddleocr call inside the PDF/image parser branch.
- **V6 scale** — replace the daemon-thread `job_runner` with a Celery worker, swap SQLite for Postgres via `DATABASE_URL`, add a `users` table and JWT auth middleware.
