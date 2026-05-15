# Contributing

Thanks for your interest in improving **AI Data Extraction Studio**.

This document covers how to set up a development environment, the code conventions used in the project, and how to open a pull request.

---

## Code of Conduct

Be kind. We follow the spirit of the [Contributor Covenant](https://www.contributor-covenant.org/).

---

## Project Layout

See the **Project Structure** section in the main `README.md`.

The repo is a monorepo with two apps:

- `apps/api` — FastAPI backend (Python 3.11+)
- `apps/web` — Next.js 14 frontend (TypeScript)

---

## Local Development Setup

### Backend

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../../.env.example ../../.env
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd apps/web
npm install
npm run dev
```

UI will be available at `http://localhost:3000`.

---

## Running Tests

```bash
cd apps/api
pytest -v
```

---

## Code Style

- **Python**: PEP 8, type hints encouraged, prefer `pathlib.Path` over `os.path`.
- **TypeScript**: strict mode enabled; prefer functional React components and hooks.
- Keep functions small and focused.
- Do not commit secrets or `.env`.

---

## Submitting a Pull Request

1. Fork the repo, create a feature branch (`git checkout -b feat/your-feature`).
2. Make your changes with clear, atomic commits.
3. Run the test suite and any relevant linters/typecheckers locally.
4. Push and open a PR against `main` with:
   - A short summary of what changed and why.
   - Screenshots or example output for UI/UX changes.
   - A note in the description if your PR addresses a Roadmap item (V2–V6).

We welcome contributions of any size — bug reports, documentation fixes, new built-in templates, real-LLM-provider implementations, and more.

---

## Reporting Bugs

Open an issue and include:

- The version / commit SHA you're running.
- Reproduction steps.
- Expected vs. actual behavior.
- Relevant logs (with secrets redacted).

Thanks for helping make this project better!
