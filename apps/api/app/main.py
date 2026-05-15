"""FastAPI entry point."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import SessionLocal, init_db
from .routers import export, files, health, jobs, results, templates
from .services.builtin_templates import seed_builtin_templates

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ai-data-extraction-studio")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Data Extraction Studio API",
        version="0.1.0",
        description=(
            "Schema-driven AI data cleaning and structured extraction platform. "
            "V1 MVP — see README for scope and roadmap."
        ),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def _startup() -> None:
        settings.ensure_dirs()
        init_db()
        db = SessionLocal()
        try:
            seed_builtin_templates(db)
        finally:
            db.close()
        log.info("AI Data Extraction Studio API ready — provider=%s", settings.model_provider)

    app.include_router(health.router)
    app.include_router(files.router)
    app.include_router(templates.router)
    app.include_router(jobs.router)
    app.include_router(results.router)
    app.include_router(export.router)

    return app


app = create_app()
