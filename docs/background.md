# Project Background

## Where this project came from

During an internship, I was handed an Excel file containing thousands of rows of natural-language descriptions of people's education and career experiences. The data had been collected from heterogeneous sources and was extremely inconsistent:

- Some rows were semi-structured JSON-like strings (`{"from":"2019","to":"2023","school":"MIT","major":"EE","degree":"MS"}`).
- Some were free-form Chinese text (`2018年9月-2022年6月 北京大学 计算机科学 本科`).
- Some were English narratives (`June 2018 - present, Google, Senior Software Engineer, search infra team`).
- Some rows mixed multiple education entries together, or mixed education and work experience in the same cell.

The business need was simple in shape: produce a clean, structured CSV with one row per record, with columns for start date, end date, school, major, degree, and whether the row was a work experience rather than an education record.

## The original one-off Python script

To solve the immediate problem, I wrote a one-off Python script. The script:

1. Read a hard-coded target column from a hard-coded Excel file path.
2. Iterated row-by-row.
3. For each row, called a wrapper around an LLM that lived inside the company's internal DataOps Git repository.
4. Parsed the model's textual response into a hard-coded set of fields.
5. Appended those fields as new columns to the original DataFrame.
6. Wrote the result to a new CSV file.

The script solved the immediate business problem, but it was deeply limited:

- The input file path, the input column name, the output field set, the prompt, and the validation rules were all hard-coded.
- There was no UI — users had to edit Python code and re-run from a terminal.
- There was no job state, no progress reporting, no retry-on-failure logic, no human-in-the-loop review, and no template system.
- It only handled one file type (Excel), and only one extraction pattern (one input row → one output row).

## What V1 of this project does

**Version 1 of AI Data Extraction Studio** turns that one-off script into a polished, fully-runnable full-stack MVP that completely covers the original internship use case:

- A **Next.js web UI** replaces the hard-coded file paths.
- A **FastAPI backend** exposes the extraction pipeline as a proper service.
- A **SQLite database** persists uploaded files, jobs, and extracted results so users can come back and review later.
- A **MockLLMClient** lets anyone run the full demo locally with **zero API keys**, while a clean `BaseLLMClient` abstraction keeps the door open for real providers later.
- A **schema validator** catches LLM output that violates the expected field types or required-ness, and the extractor automatically retries failed rows with feedback.
- The **results page** shows every extracted row alongside its source text, lets the user filter by success/failed status, edit any field inline, and re-run failed rows.
- An **exporter** writes a CSV or XLSX with the original columns preserved and the extracted columns appended — exactly mirroring what the original internship script produced.

## What's next

V1 deliberately covers only the original internship problem, end-to-end and well. Later versions (V2 through V6) expand the scope into a general-purpose AI extraction platform — see the **Roadmap** section of the README for the full plan.

The progression looks like this:

```
Real internship problem
        ↓
One-off Python Excel cleaning script
        ↓
V1 full-stack AI Excel extraction MVP   ← you are here
        ↓
V2: Custom schema builder
V3: Real LLM providers (OpenAI, Anthropic, …)
V4: DOCX / PDF / TXT / Markdown + document-wise mode
V5: OCR + advanced chunking
V6: Auth, teams, Postgres, queues, cloud deploy
        ↓
General-purpose AI unstructured data extraction platform
```
