<div align="center">

# AI Data Extraction Studio

**A schema-driven, AI-powered data cleaning and structured extraction platform.**

*Turn messy natural-language text in your spreadsheets into clean, structured tables.*

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=nextdotjs&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-V1%20MVP-orange)
![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen)

[English](./README.md) · [简体中文](./README.zh-CN.md)

</div>

---

## 📸 Screenshots

> Screenshots will be captured after the first manual demo. The walkthrough in [How to Use](#-how-to-use-step-by-step) describes exactly what each page looks like.

```
┌────────────────────────────────────────────────────────┐
│  [Home]   →   [Upload]   →   [Run]   →   [Results]    │
│                                                        │
│   Landing      Drop CSV     Pick column    Edit /      │
│   page         preview      run job        export      │
└────────────────────────────────────────────────────────┘
```

---

## 📖 Project Background

> This project was inspired by a real data cleaning problem I encountered during an internship.
>
> At that time, I was working with an Excel file that contained messy natural-language descriptions of education and career experiences. The data was highly inconsistent: some rows looked like semi-structured JSON strings, some were free-form Chinese text, some were English descriptions, and some mixed education history with work experience.
>
> To solve this problem, I built a Python script that read the target column from the Excel file, called an internal AI model wrapper from the company's DataOps Git repository, extracted structured fields such as start date, end date, school, major, degree, and whether the record was work experience, and then wrote the extracted results back to a new CSV file.
>
> That script solved the immediate business problem, but it was still a one-off pipeline: the input column, output fields, prompt, validation rules, and file paths were all hard-coded.
>
> **Version 1 of AI Data Extraction Studio** productizes that original script into a runnable full-stack MVP with a web interface, backend API, mock AI extraction, validation, result review, and export support.

The project's evolution is intentionally staged:

```
Real internship problem
        ↓
One-off Python Excel cleaning script
        ↓
V1 full-stack AI Excel extraction MVP   ← this repo, today
        ↓
Future complete AI unstructured data extraction platform (V2–V6 in Roadmap)
```

A longer write-up lives in [`docs/background.md`](./docs/background.md).

---

## 🎯 V1 Scope

V1 deliberately covers **one use case** completely and well: the original internship workflow. Everything else is on the roadmap and clearly marked.

| Feature | V1 | Notes |
|---|:--:|---|
| Upload `.xlsx` / `.csv` | ✅ | |
| Live preview of headers + 20 rows | ✅ | |
| Row-wise extraction (one row → one record) | ✅ | |
| Built-in template: *Education Experience Cleaner* | ✅ | Fields: `from`, `to`, `school`, `major`, `scholar`, `is_work_experience` |
| Mock LLM client (no API keys required) | ✅ | |
| Pydantic schema validation + retry on failure | ✅ | |
| Job runner with live progress | ✅ | Background thread + SQLite |
| Result review with inline edit | ✅ | |
| Re-run failed rows | ✅ | |
| Export CSV / XLSX with original columns + extracted columns | ✅ | |
| Bilingual docs (EN / 中文) | ✅ | |
| Docker / docker-compose | ✅ | |
| Backend tests | ✅ | |
| Custom schema builder | ❌ | V2 |
| Real LLM providers (OpenAI, Anthropic, …) | ❌ | V3 |
| `.docx` / `.pdf` / `.txt` / `.md` support | ❌ | V4 |
| Document-wise extraction (one doc → many records) | ❌ | V4 |
| OCR for scanned PDFs | ❌ | V5 |
| Auth / teams / cloud | ❌ | V6 |

---

## ✨ Features (V1)

- **🪶 Zero-config demo** — clone, install, run. The `MockLLMClient` does realistic extraction without any external API keys.
- **🧩 Schema-driven validation** — every extracted record is validated against a Pydantic model built dynamically from the template's field definitions.
- **🔁 Automatic retry with feedback** — when the model returns invalid JSON or a record fails validation, the extractor automatically retries with the error message embedded in the next prompt.
- **🖊️ Human-in-the-loop review** — inspect every row's source text alongside the AI's extraction; edit any field inline; re-run failed rows on demand.
- **📦 Clean export** — original columns are preserved; extracted fields are appended, exactly as the original internship script did.
- **🧱 Clean abstractions** — `BaseLLMClient` is ready to host real providers in V3 without touching the rest of the pipeline.

---

## 🛠️ Tech Stack

**Backend**

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x + SQLite
- Pydantic 2
- pandas, openpyxl
- pytest

**Frontend**

- Next.js 14 (App Router)
- TypeScript (strict)
- Tailwind CSS
- shadcn/ui
- TanStack Table
- SWR (polling)
- react-hook-form + zod

**Tooling**

- Docker + docker-compose
- MIT License

---

## 📂 Project Structure

```
ai-data-extraction-studio/
├── apps/
│   ├── api/                              # FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py                   # FastAPI app entry
│   │   │   ├── config.py                 # Env-driven config
│   │   │   ├── db.py                     # SQLAlchemy session
│   │   │   ├── models/                   # DB models
│   │   │   ├── schemas/                  # Pydantic DTOs
│   │   │   ├── routers/                  # API endpoints
│   │   │   ├── services/                 # Core extraction logic
│   │   │   │   ├── excel_parser.py
│   │   │   │   ├── prompt_builder.py
│   │   │   │   ├── llm_client.py         # MockLLMClient + ABC
│   │   │   │   ├── validator.py
│   │   │   │   ├── extractor.py
│   │   │   │   ├── job_runner.py
│   │   │   │   ├── exporter.py
│   │   │   │   └── builtin_templates.py
│   │   │   └── utils/
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── web/                              # Next.js frontend
│       ├── app/
│       │   ├── page.tsx                  # Landing
│       │   ├── upload/page.tsx
│       │   ├── run/page.tsx
│       │   ├── jobs/[jobId]/page.tsx
│       │   └── results/[jobId]/page.tsx
│       ├── components/
│       ├── lib/api.ts                    # All HTTP calls
│       ├── types/api.ts
│       └── Dockerfile
│
├── docs/                                  # Architecture + background
├── examples/                              # Sample CSV / XLSX
├── scripts/                               # Helper scripts
├── storage/{uploads,exports}              # Runtime file storage
├── data/                                  # SQLite DB lives here
├── .env.example
├── docker-compose.yml
├── README.md                              # ← you are here
└── README.zh-CN.md
```

---

## ⚡ Quick Start

You can run the project **locally** (two terminals) or via **Docker** (one command). Both paths produce the same demo.

> **Prerequisites:** Python 3.11+, Node.js 20+, and either npm or pnpm. For Docker: Docker Desktop or Docker Engine with Compose V2.

### Option A — Local Development

#### 1. Clone and prepare the environment file

```bash
git clone https://github.com/<your-username>/AI-Driven_Data_Cleaning_Pipeline.git
cd AI-Driven_Data_Cleaning_Pipeline
cp .env.example .env
```

You don't need to edit `.env` — the defaults work out of the box with the Mock LLM.

#### 2. Start the backend (Terminal 1)

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Open <http://localhost:8000/docs> to see the interactive API explorer.

#### 3. Start the frontend (Terminal 2)

```bash
cd apps/web
npm install
npm run dev
```

You should see:

```
✓ Ready in 1.4s
- Local:    http://localhost:3000
```

#### 4. Open the app

Navigate to <http://localhost:3000> in your browser.

### Option B — Docker

```bash
docker compose up --build
```

This will start both services. Once you see `Application startup complete.` (backend) and `Ready` (frontend), open:

- Frontend: <http://localhost:3000>
- Backend API: <http://localhost:8000>
- API docs: <http://localhost:8000/docs>

---

## 🧑‍🏫 How to Use (step-by-step)

This walkthrough takes you from a fresh install to a fully exported CSV in about **3 minutes** using the bundled sample file.

### Step 0 — Start the app

Use either path above (local or Docker) and confirm the backend is on `:8000` and the frontend is on `:3000`.

### Step 1 — Open the landing page

Visit <http://localhost:3000>. You'll see the AI Data Extraction Studio hero with a **"Start Extraction"** button.

> ✅ **What you should see:** Project title, tagline, the V1 workflow strip (`Upload → Pick column → Run → Review → Export`), and a green "Start Extraction" call-to-action button.

Click **Start Extraction**.

### Step 2 — Upload the sample file

You're now at `/upload`.

1. Click **"Choose file"** (or drag-and-drop) and pick `examples/education_experience_sample.csv` from this repo.
2. The page automatically uploads the file and shows a preview table with **10 rows × 3 columns** (`id`, `name`, `experience`).

> ✅ **What you should see:** A preview table where the `experience` column contains messy text such as `2018年9月-2022年6月 北京大学 计算机科学与技术 本科` and `{"from":"2019","to":"2023","school":"MIT","major":"EE","degree":"MS"}`. A "Continue →" button appears below the preview.

Click **Continue**.

### Step 3 — Configure the extraction

You're now at `/run`.

1. **Input column** dropdown → select `experience`.
2. **Template** dropdown → it should already show *Education Experience Cleaner* (the only V1 built-in template).
3. **Max rows** input → leave the default (`100`) or set it to `10` to process just the sample.
4. Click **Run Extraction**.

> 💡 **Tip:** The Template card shows you exactly which fields will be extracted: `from`, `to`, `school`, `major`, `scholar`, `is_work_experience`.

### Step 4 — Watch the job run

You'll be redirected to `/jobs/<jobId>`. The page polls the backend every 2 seconds.

> ✅ **What you should see:**
> - A progress bar advancing from 0% → 100%.
> - Counter cards: **Total / Processed / Success / Failed**.
> - For the sample CSV, expect roughly **9 successes** and **0–1 failed** rows (the mock LLM intentionally fails on one ambiguous row to demonstrate the retry/failure path).
> - When status becomes `completed`, the page automatically redirects to `/results/<jobId>`.

### Step 5 — Review the extracted results

You're now at `/results/<jobId>`.

- The table shows one row per source row, with the original `input_text` followed by the extracted fields (`from`, `to`, `school`, `major`, `scholar`, `is_work_experience`).
- Use the **All / Success / Failed** tabs at the top to filter.
- Click the **Edit** icon on any row to open the edit dialog — change any field, save, and the result is updated in the database.
- Click **Retry failed** to re-queue any failed rows through the extractor.

> 💡 **Tip:** Failed rows show a red badge. Hover the badge to see the validation error message.

### Step 6 — Export the cleaned data

In the top right of the results page:

- Click **Export CSV** — downloads a CSV containing the original columns (`id`, `name`, `experience`) followed by the six extracted columns.
- Click **Export XLSX** — same thing as an Excel file.

> ✅ **What the exported file looks like (CSV preview):**
>
> ```csv
> id,name,experience,from,to,school,major,scholar,is_work_experience
> 1,张伟,2018年9月-2022年6月 北京大学 计算机科学与技术 本科,2018-09,2022-06,北京大学,计算机科学与技术,Bachelor,false
> 2,Alice Johnson,"2015/09 - 2019/06, Stanford University, …",2015-09,2019-06,Stanford University,Computer Science,Bachelor,false
> ...
> ```

### 🎉 You're done

That's the original internship workflow, productized — fully runnable on your laptop with no external dependencies and no API keys.

---

## 🌱 Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `MODEL_PROVIDER` | `mock` | Only `mock` is supported in V1 |
| `MODEL_NAME` | `mock-extractor` | Cosmetic; surfaced in `/api/health` |
| `MAX_RETRIES` | `2` | Per-row retry budget on validation failure |
| `TEMPERATURE` | `0` | Reserved for V3 real providers |
| `MAX_CONCURRENCY` | `3` | Threads in the per-job executor |
| `DATABASE_URL` | `sqlite:///./data/app.db` | SQLAlchemy URL |
| `UPLOAD_DIR` | `./storage/uploads` | Where uploaded files live |
| `EXPORT_DIR` | `./storage/exports` | Where exports are staged |
| `BACKEND_CORS_ORIGINS` | `http://localhost:3000` | Allowed CORS origins (comma-separated) |
| `NEXT_PUBLIC_API_BASE` | `http://localhost:8000` | Frontend's pointer to the backend |
| `OPENAI_API_KEY` | _(unset)_ | Reserved for V3 |
| `ANTHROPIC_API_KEY` | _(unset)_ | Reserved for V3 |

---

## 🔌 Built-in Template (V1)

**Name:** *Education Experience Cleaner*
**Mode:** row-wise

| Field | Type | Required | Description |
|---|---|:--:|---|
| `from` | string | ❌ | Start date (e.g. `2018-09` or `2018`) |
| `to` | string | ❌ | End date or `present` |
| `school` | string | ❌ | Institution or company name |
| `major` | string | ❌ | Field of study (education) or position (work) |
| `scholar` | string | ❌ | Degree (`Bachelor`, `Master`, `PhD`) |
| `is_work_experience` | boolean | ✅ | `true` if the row describes a work experience |

Examples and the instruction text are seeded into the database on first startup. You can inspect or fetch the template via `GET /api/templates`.

---

## 🌐 API Overview

All endpoints are prefixed with `/api`. Full interactive docs at <http://localhost:8000/docs>.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | Liveness probe + active LLM provider |
| `POST` | `/api/files/upload` | Upload an `.xlsx` / `.csv`; returns `{file_id, headers, preview_rows, total_rows}` |
| `GET` | `/api/templates` | List all templates (built-in flagged) |
| `GET` | `/api/templates/{id}` | Template detail |
| `POST` | `/api/jobs` | Create + start an extraction job |
| `GET` | `/api/jobs/{id}` | Job status + progress counters |
| `POST` | `/api/jobs/{id}/retry-failed` | Re-queue failed rows |
| `GET` | `/api/jobs/{id}/results` | Paginated results (filter by status) |
| `PATCH` | `/api/results/{id}` | Manually edit one result |
| `GET` | `/api/jobs/{id}/export?format=csv\|xlsx` | Download merged file |

---

## 🧪 Testing

```bash
cd apps/api
pytest -v
```

Covers:

- Excel / CSV parsing
- Prompt builder output shape
- Pydantic validator (required fields, type errors, enum bounds)
- MockLLMClient determinism
- End-to-end job runner
- CSV / XLSX exporter

---

## 🗺️ Roadmap

Each item is **planned**, not pretended-implemented.

| Version | Theme | Planned features |
|---|---|---|
| **V2** | Custom schemas | User-defined fields, prompts, examples, and reusable templates; template import/export |
| **V3** | Real LLM providers | OpenAI, Anthropic, DeepSeek implementations of `BaseLLMClient`; cost estimation; smarter retry-on-invalid-JSON |
| **V4** | More file types | `.docx`, `.txt`, `.md`, text-based `.pdf`; document-wise extraction (one doc → many records) |
| **V5** | OCR & long docs | OCR for scanned PDFs; advanced chunking; multi-record extraction from long documents |
| **V6** | Production deploy | Auth, team workspaces, PostgreSQL, S3 / cloud storage, Celery/Redis queues, deployment templates |

---

## ⚠️ Limitations

- Only `.xlsx` and `.csv` are accepted in V1 (no DOCX/PDF/TXT/MD yet).
- Only row-wise extraction is supported (no document-wise mode yet).
- Only one built-in template (*Education Experience Cleaner*); no custom schema builder yet.
- `MockLLMClient` is the only working LLM client — it's heuristic-based and is not a substitute for a real model. Real providers land in V3.
- The job queue is in-process (threads inside the API container). Restarting the API mid-job will lose unfinished work. Queue persistence is V6.
- No authentication; intended for single-user local use.
- No OCR yet — scanned PDFs are not supported.
- Frontend screenshots in this README are placeholders until manual capture.

---

## 🩹 Troubleshooting

**`Address already in use` on port 8000 or 3000**
Another process is using the port. Either stop it or pass a different port: `uvicorn app.main:app --port 8001` / `npm run dev -- -p 3001`. If you change the API port, update `NEXT_PUBLIC_API_BASE` in `.env`.

**`ModuleNotFoundError: No module named 'app'`**
Make sure you're running `uvicorn app.main:app` **from inside `apps/api/`** (not from the repo root).

**Frontend shows "Failed to fetch" on every page**
The frontend can't reach the backend. Check that:
1. The backend is running at the URL set in `NEXT_PUBLIC_API_BASE`.
2. The backend's `BACKEND_CORS_ORIGINS` includes the frontend's URL.

**`sqlite3.OperationalError: unable to open database file`**
The `data/` directory doesn't exist (or isn't writable). Create it: `mkdir -p data`.

**`npm install` fails on Node 18**
Next.js 14 supports Node 18.17+, but Node 20+ is recommended. Upgrade with `nvm install 20 && nvm use 20`.

---

## 🤝 Contributing

PRs are welcome. See [`CONTRIBUTING.md`](./CONTRIBUTING.md).

Especially good first contributions:

- Add a new built-in template (work experience cleaner, resume parser, …).
- Implement a real-provider `LLMClient` for the V3 roadmap.
- Improve the MockLLMClient's heuristic coverage on edge-case inputs.
- Write more tests.

---

## 📜 License

[MIT](./LICENSE) © 2026 AI Data Extraction Studio contributors.

---

## 🙏 Acknowledgements

- The original internship problem, which made the need for this kind of tool concrete.
- The open-source ecosystems behind FastAPI, Next.js, SQLAlchemy, Pydantic, Tailwind CSS, shadcn/ui, and TanStack — without which this project would not exist.
